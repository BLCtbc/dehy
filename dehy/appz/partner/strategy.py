from oscar.apps.partner import strategy, prices


class Selector(object):
    """
    Custom selector class to returns a US strategy
    """

    def strategy(self, request=None, user=None, **kwargs):
        return USStrategy()


class USStrategy(strategy.UseFirstStockRecord, strategy.DeferredTax, strategy.StockRequired, strategy.Structured):
    """
    Typical US strategy for physical goods.  Note we use the ``DeferredTax``
    mixin to ensure prices are returned without tax.

    - Use first stockrecord
    - Enforce stock level
    - Taxes aren't known for prices at this stage
    """