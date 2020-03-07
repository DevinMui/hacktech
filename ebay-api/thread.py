from api import API
from time import sleep

# api should be global so threads can have access

api = API()

# maxAmount should be in double format
def thread(_id: str):
    currBid = None
    while True:
        # find orders
        queue = db.queues.find_one({"_id": _id})

        # sort order queue by user param
        sort(queue)

        if currBid:
            bid = api.get(f"/buy/offer/v1_beta/bidding/{order.ebayId}")

            # we lost bid
            if not bid["highBidder"]:
                currBid = None
            # we won!
            elif bid["auctionStatus"] is "ENDED":
                return
            else:
                sleep(60)
                continue

        # delete if outbidded
        for order in queue:
            # get info
            item = api.get(f"/buy/browse/v1/item/{order.ebayId}")

            # the user put a bid on an item w/o us knowing
            try:
                bid = api.get(f"/buy/offer/v1_beta/bidding/{order.ebayId}")
                # we lost!
                if not bid["highBidder"]:
                    currBid = None
                    queue.dequeue()
                # we won the bid!
                elif bid["auctionStatus"] is "ENDED":
                    return
                else:
                    currBid = bid
                    queue.dequeue()

            # the user didnt put a bid on an item w/o us knowing
            except Exception:
                # if item is too expensive
                if item["currentPrice"] > queue.maxPrice:
                    currBid = None
                    queue.dequeue()
                # we won
                elif item["auctionStatus"] is "ENDED":
                    currBid = None
                    queue.dequeue()
                else:
                    # place bid
                    payload = {
                        "maxAmount": {
                            "currency": "USD",
                            "value": str(order["maxAmount"]),
                        }
                    }
                    bid = api.post(
                        f"/buy/offer/v1_beta/bidding/{order.ebayId}/place_proxy_bid",
                        json=payload,
                    )
                    currBid = bid
                    queue.dequeue()

        # kill thread
        if not currBid and queue.empty():
            return

    sleep(60)  # 1440 req/day (over ebay limit)

