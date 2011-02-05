.. _index:

===========
My Bad Wiki
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

Some javascript:

.. code :: javascript

    for(var i = 0, l = it.length; i < l; i++){
        console.log(this.isRad);
    }

Wow, html inline:
    
.. code :: html

   <div class="bar">baz</div>

CSS is easy:
   
.. code :: css 

    #foo {
        color: red;
    }

That wasn't _live_ per se. But I can make things **bold**

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

A Table?
--------

Wtf is going on here:

:foo: This is a test
:bar: More testing
:muchLonger: See how it aligns
:o: My that's a short label
:gee: This is a particularly long cell and blah blah blah blah blah blah blah.

Explaining reST within reST
---------------------------

Entirely possible.

.. code :: markdown

  =======
  Heading
  =======
  
  List:
  
    * one
    * two
       * three
       * four
    * five

Cool. What Next?
----------------

Don't even pretend to be done

+-----------------------+-------------------------------------------------------+
|  **tables**           | **matter to folks** really                            |
+-----------------------+-------------------------------------------------------+
| weird                 |   yes, table syntax is bloody weird.                  |
+-----------------------+-------------------------------------------------------+
| link                  |  :ref:`wow <foo/bar>`                                 |
+-----------------------+-------------------------------------------------------+

There has got to be a better way for tables.

Also tables are dumb.

