What is Reek?
-------------

Reek is a set of building blocks for managing content in a Django environment. It consists of four (almost entirely) individual - but related - parts:

1. A dynamic urlconf so site administrators can effectively rearrange the entire site (because no matter your counter-arguments, they want this badly). It provides custom [class-based views](https://docs.djangoproject.com/en/dev/topics/class-based-views/) (CBV) which can be targeted from the admin. It also gives you a declarative way of defining URLs.
2. An admin! Because you if you tackle one problem, tackle them all O:) 
3. A mechanism for creating a small publish/review workflow (because "allowing an intern to publish directly is silly"). These can be applied to any Django model. 
4. A content Field for your models which renders to HTML and has a basic editor for the admin which can include a preview (because your client is adamant about WYSIWYG).

Reek is currently a pet project and should only be used to toy with content management concepts without having to extensively hack on an existing CMS.

Aren't there enough excellent CMSes?
------------------------------------

Yes, there are, but most tend to get in your way when you disagree with a feature or want to use it outside of the CMS. Reek tries to be just a basic set of individual tools in your kit so you can build your own. And because nobody can take you seriously without ever having thought about rolling your own CMS ;-)

Why is it called Reek?
----------------------

Because [every CMS smells](http://hawksworx.com/blog/i-can-smell-your-cms-a-talk-at-fronteers/) in some way, no matter how you sugarcoat it.
