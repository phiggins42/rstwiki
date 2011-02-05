.. _foo/index:

Weird, huh
==========

Only top level stuff needs an /index.

There should only be one :ref:`master index <index>` ... And Sphinx (afaik) doesn't like /name for TOC reasons.
    
So, roots need /index. eg: :ref:`this page <foo/index>` ... linking to :ref:`just foo <foo>` should pretend it's :ref:`thie same <foo/index>`

**FIXME**: /edit/\w+ should really always /edit/\w+/index instead. Only on root.
