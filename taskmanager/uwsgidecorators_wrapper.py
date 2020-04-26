"""
Wrapper module to uwsgidecorators module.

Code borrowed from `uwsgidecorators-fallback` package.

Copyright 2016-2019 Lars van de Kerkhof
"""


class BaseDecorator(object):
    @property
    def spool(self):
        return self.f

    def __init__(self, f):
        self.f = f

    def __call__(self, *args, **kwargs):
        return self.f(*args, **kwargs)


class BaseDecoratorWithArguments(object):
    def __init__(self, *args, **kwargs):
        # because we are so fake we don't give a shit about the arguments
        pass

    def __call__(self, f):
        # just pretend no decorator was there at all haha
        return f


class Spooler:
    def __init__(self, f=None, pass_arguments=False):
        # this is strange because spool can be used either with or without
        # keyword arguments.
        if f is not None and callable(f):

            def wrapped_func(**kwargs):
                return f(kwargs)

            self.f = f

        else:
            self.pass_arguments = pass_arguments

    def __call__(self, f=None, **kwargs):
        # spool is crap because it could be called with or without arguments.
        if f is not None and callable(f):
            if self.pass_arguments:  # with pass_arguments spool is just normal
                return BaseDecorator(f)
            else:  # keyword arguments are passed as a dict to spool

                def wrapped_func(**kwargs):
                    return f(kwargs)

                return BaseDecorator(wrapped_func)
        else:
            self.f(**kwargs)

    @property
    def spool(self):
        return self.f


try:
    from uwsgidecorators import *
except ModuleNotFoundError as e:
    if e.name == "uwsgi":
        # probably running without of uWSGI
        class lock(BaseDecorator):
            pass

        class spool(Spooler):
            pass

        class cron(BaseDecoratorWithArguments):
            pass

        class timer(BaseDecoratorWithArguments):
            pass

    else:
        raise e
