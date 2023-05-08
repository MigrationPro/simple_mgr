import argparse

from cart import Cart
from exporter import get_exporter
from importer import get_importer
from utils import find_logger

logger = find_logger(__name__)


def process(source: Cart, target: Cart) -> None:
    """
    This function imports data from a source cart and exports it to a target cart.

    Args:
      source: The source cart.
      target: The target cart.

    Returns:
      None.
    """
    importer = get_importer(cart=source)
    source_data = importer.start()
    logger.info("Source data count %s", len(source_data))

    exporter = get_exporter(source_data, cart=target)
    number_of_entity_count = exporter.start()
    logger.info("Number of the entities migrated %s", number_of_entity_count)


if __name__ == "__main__":
    # extract the values FOR these variables from the command line options (flags)
    # python main.py --source_url http://source.com --source_token SOURCE
    # --target_url http://target.com --target_token TARGET

    # create the command line parser
    parser = argparse.ArgumentParser()
    # add the command line options (flags)
    parser.add_argument('--source_url', dest='source_url', type=str, default=None, help='Source URL')
    parser.add_argument('--source_token', dest='source_token', type=str, default=None, help='Source Token')
    parser.add_argument('--target_url', dest='target_url', type=str, default=None, help='Target URL')
    parser.add_argument('--target_token', dest='target_token', type=str, default=None, help='Target Token')
    # parse the command line arguments
    args = parser.parse_args()

    # create the source and target carts
    source_cart = Cart(args.source_url, args.source_token)
    target_cart = Cart(args.target_url, args.target_token)
    process(source_cart, target_cart)
