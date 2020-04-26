"""Define utils for logging."""

import logging


class NoTerminatorStreamHandler(logging.StreamHandler):
    """
    A stream handler.

    Extends the `logging.StreamHandler` handler.

    It will emit the records to the stream, without writing the terminator.

    It is used to work correctly with django.core.management.OutputWrapper,
    that already appends the ending character to streams, in its write.

    This is used when the stdout parameter is set to a StringIO for call_command.
    """

    def __key(self):
        return self.name, self.level

    def __hash__(self):
        """Hash method."""
        return hash(self.__key())

    def __eq__(self, other):
        """Equal method."""
        return isinstance(self, type(other)) and self.__key() == other.__key()

    def emit(self, record):
        """
        Emit a record. Does not emit a terminator.

        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline.  If
        exception information is present, it is formatted using
        traceback.print_exception and appended to the stream.  If the stream
        has an 'encoding' attribute, it is used to determine how to do the
        output to the stream.
        """
        try:
            msg = self.format(record)
            stream = self.stream
            stream.write(msg)
            self.flush()
        except Exception:  # noqa
            self.handleError(record)
