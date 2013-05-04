def raises(exception):
    """Marks test to expect the specified exception.
    Call assertRaises internally"""
    def test_decorator(fn):
        def test_decorated(self, *args, **kwargs):
            self.assertRaises(exception, fn, self, *args, **kwargs)
        return test_decorated
    return test_decorator


def not_raises(exception):
    def test_decorator(fn):
        def test_decorated(self, *args, **kwargs):
            try:
                fn(self, *args, **kwargs)
            except exception:
                self.fail(
                    '%s raised %s unexpectedly!' %
                    (fn.__name__, exception.__name__))
        return test_decorated
    return test_decorator
