from api import API
from time import sleep
import threading
from bson.objectid import ObjectId

# start a thread for each order
def startThread(api, atlas, queueId: str):
    x = threading.Thread(target=bidOnQueue, args=(api, atlas, queueId))
    x.daemon = True
    x.start()


# maxAmount should be in double format
def bidOnQueue(api, atlas, _id: str):
    currBid = None
    sleepTime = 60
    while True:
        # find orders

        queue = atlas.findQueue(_id)
        if not queue["start"]:
            return

        # get new info
        for order in queue["orders"]:
            item = api.get(f"/buy/browse/v1/item/{order['itemId']}")
            atlas.updateOrder(order["_id"], item)

        # sort order queue by user param
        sorted(queue["orders"], key=lambda k: k["currentPrice"])

        # we have a bid right now
        if currBid:
            bid = api.get(f"/buy/offer/v1_beta/bidding/{order['itemId']}")

            # we lost bid
            if not bid["highBidder"]:
                currBid = None
            # we won!
            elif bid["auctionStatus"] is "ENDED":
                # set a flag in the mongo?
                return
            else:
                sleep(sleepTime)
                continue

        # delete if outbidded
        for order in queue["orders"]:
            # the user put a bid on an item w/o us knowing
            try:
                bid = api.get(f"/buy/offer/v1_beta/bidding/{order['itemId']}")
                # we lost!
                if not bid["highBidder"]:
                    currBid = None
                    atlas.dequeue(order["_id"])
                # we won!
                elif bid["auctionStatus"] is "ENDED":
                    return
                # bid is still on going
                else:
                    currBid = bid
                    sleep(sleepTime)
                    continue

            except Exception:
                # if item is too expensive
                if order["currentPrice"] > queue["max_bid"]:
                    currBid = None
                    atlas.dequeue(order["_id"])
                # auction is over
                elif item["auctionStatus"] is "ENDED":
                    currBid = None
                    atlas.dequeue(order["_id"])
                else:
                    # place bid
                    payload = {
                        "maxAmount": {
                            "currency": "USD",
                            "value": str(queue["max_bid"]),
                        }
                    }
                    bid = api.post(
                        f"/buy/offer/v1_beta/bidding/{order['itemId']}/place_proxy_bid",
                        json=payload,
                    )
                    currBid = bid
                    atlas.dequeue(order["_id"])

        # kill thread
        if not currBid and queue.empty():
            return

    sleep(sleepTime)  # 5000 requests / day

