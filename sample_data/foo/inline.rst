.. _foo/inline:

Inline API and Code
====================

.. contents ::

live-code blocks simply render raw. Try to pick a unique id if using DomNodes with id's:

.. live-code ::

   <p id="bar">foo</p>
   <script>
       dojo.ready(function(){    
           dojo.query("#bar").onclick(function(e){ alert('clicked #bar'); })
       });
   </script>



Checkout :ref:`CodeGlass style examples <foo/codeglass>` too




And a few more:

dojo.byId
=========

.. api-inline :: dojo.byId

dojo.replace
============

.. api-inline :: dojo.replace

dojo.NodeList
=============

.. api-inline :: dojo.NodeList
