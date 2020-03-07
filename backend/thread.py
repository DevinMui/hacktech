from api import API
from time import sleep
import threading
from bson.objectid import ObjectId

# start a thread for each order
def startThread(api, atlas, queueId: str):
    x = threading.Thread(target=bidOnQueue, args=(api, atlas, queueId))
    x.start()


# maxAmount should be in double format
def bidOnQueue(api, atlas, _id: str):
    currBid = None
    sleepTime = 60
    while True:
        # find orders

        queue = atlas.findQueue(_id)

        # get new info
        for order in queue:
            item = api.get(f"/buy/browse/v1/item/{order['itemId']}")
            atlas.updateOrder(order["_id"], item)

        # sort order queue by user param
        # TODO
        sorted(queue)

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
        for order in queue:
            # the user put a bid on an item w/o us knowing
            try:
                bid = api.get(f"/buy/offer/v1_beta/bidding/{order['itemId']}")
                # we lost!
                if not bid["highBidder"]:
                    currBid = None
                    atlas.dequeue(order["_id"])
                # we won the bid!
                elif bid["auctionStatus"] is "ENDED":
                    # set flag
                    return
                else:
                    currBid = bid
                    atlas.dequeue(order["_id"])

            # the user didnt put a bid on an item w/o us knowing
            except Exception:
                # if item is too expensive
                if order["currentPrice"] > queue["maxBid"]:
                    currBid = None
                    atlas.dequeue(order["_id"])
                # auction is over
                elif item["auctionStatus"] is "ENDED":
                    atlas.dequeue(order["_id"])
                else:
                    # place bid
                    payload = {
                        "maxAmount": {
                            "currency": "USD",
                            "value": str(order["maxAmount"]),
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

    sleep(sleepTime)  # 1440 req/day (over ebay limit)

