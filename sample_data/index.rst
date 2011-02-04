.. _index:

===========
My Rad Wiki
===========

I think reST is the greatest ever.

.. contents ::

This is Why
-----------

It's silly, but I can :ref:`link to anything <foo/bar>` inline, and do all sorts of other crazyness.

Second Point
------------

This is a custom directive:

.. api-ref :: dojo.query

Inline Examples
---------------

Live embedded code blocks. Simple:

.. javascript ::

    for(var i = 0, l = it.length; i < l; i++){
        console.log(this.isRad);
    }
    
That wasn't _live_ per se. But I can make thing **bold**

Also, there are ways to `really` do custom inline examples:

.. code-example ::

    .. javascript ::
            
            <script>
                alert('win')
            </script>
            
Basic Lists and Shit
--------------------

A list:

    * one
    * two 
    * three
        * three one
        * three two
    * four
        * four one
        * four two
            * ohhhhh
    * five 

Some headings?

:foo: This is a test
:bar: More testing
:muchLonger: See how it aligns
:o: My that's a short label
:gee: This is a particularly long cell and blah blah blah blah blah blah blah.

