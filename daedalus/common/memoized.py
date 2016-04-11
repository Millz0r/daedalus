#pylint: disable=invalid-name
'''Memoization, based on https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize'''

import collections
import functools

class memoized(object):
    '''Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    '''
    cache = dict()

    def __init__(self, func):
        self.func = func
        self.func_name = func.__name__
        self.cache[self.func_name] = collections.OrderedDict()

    def __call__(self, *args, **kwargs):
        if not isinstance(args, collections.Hashable):
            raise TypeError('Must be called with hashable arguments')

        # Since kwargs represent configuation options to the functions
        # we don't use them as part of the cache key, but we do call with them.
        if args in self.cache[self.func_name]:
            return self.cache[self.func_name][args]
        else:
            value = self.func(*args, **kwargs)
            self.cache[self.func_name][args] = value
            return value

    def __repr__(self):
        '''Return the function's docstring.'''
        return self.func.__doc__

    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        return functools.partial(self.__call__, obj)

    @classmethod
    def get_list(cls, func_name):
        '''Returns the cached values for a given function.'''
        return cls.cache[func_name].values()

    @classmethod
    def clear_cache(cls):
        '''Dumps the cache for each function declared with @memoized.'''
        # There's a memoized instance for each @memoized function so we can't just
        # drop cls.cache, we need to keep the keys and clear the child dicts.
        for memo in cls.cache.values():
            memo.clear()
