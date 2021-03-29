Design notes
====

Index.vue works as the theme router. Default theme can be used as good example template to create new themes. Let new themes come up, and old themes natually fade out.

The design is templating over inheriting. Apparently, this design causes repeating codes. The benefit here is it's independent to hold different design styles, that come from different designers and clients. Demo pages are leaf elements, we do not inherit from it, but template from good examples.
