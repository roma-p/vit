
class CheckoutType:
    commit = "commit"
    branch = "branch"
    tag = "tag"

class Checkout(object):

    def __init__(self, checkout_type, checkout_value):
        self.checkout_type = checkout_type
        self.checkout_value = checkout_value

    def __str__(self):
        return "checkout {} -> {}".format(
            self.checkout_type,
            self.checkout_value
        )
