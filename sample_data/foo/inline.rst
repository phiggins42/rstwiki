.. _foo/inline:

Inline API and Code
===================

live-code blocks simply render raw. Try to pick a unique id if using DomNodes with id's:

.. live-code ::

   <p id="bar">foo</p>
   <script>
       dojo.ready(function(){    
           dojo.query("#bar").onclick(function(e){ alert('clicked #bar'); })
       });
   </script>

The above "foo" will alert when clicked.

This is an "api-link" directive:

.. api-link :: dojo.forEach

This is an api-inline directive:

.. api-inline :: dojo.query

And a few more:

.. api-inline :: dojo.byId
.. api-inline :: dojo.replace
.. api-inline :: dojo.NodeList








