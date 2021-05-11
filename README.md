# FlaskApp
Flask web app that will read from a database containing spells from dungeons and dragons.
The web app has a search bar and some conditions. These include search types such as search for spells by id, name, etc... and min and max levels.
It displays the results from the queries in a table with toggleable columns which can be toggled using the collaspable div that contains checkboxes.

Image srcs:
Dungeons&DragonsDice.png: https://pixabay.com/illustrations/d20-dice-dungeons-dragons-2699387/
DnD_Logo.png: https://dnd.wizards.com/articles/features/fan-site-kit
Favicon was drawn by me.



SQL designer:
<!-- <?xml version="1.0" encoding="utf-8" ?>
SQL XML created by WWW SQL Designer, https://github.com/ondras/wwwsqldesigner/
Active URL: https://ondras.zarovi.cz/sql/demo/ 
<sql>
<datatypes db="sqlite">
	<group label="Affinity">
		<type label="Text" default="" length="1" sql="TEXT" quote="'" color="rgb(255,200,200)"/>
		<type label="Numeric" default="0" length="0" sql="NUMERIC" quote="" color="rgb(238,238,170)"/>
		<type label="Integer" default="0" length="0" sql="INTEGER" quote="" color="rgb(238,238,170)"/>
		<type label="Real" default="0" length="0" sql="REAL" quote="" color="rgb(238,238,170)"/>
		<type label="None" default="" length="0" sql="NONE" quote="" color="rgb(200,255,200)"/>
	</group>
</datatypes><table x="10" y="10" name="spells">
<row name="id" null="1" autoincrement="1">
<datatype>TEXT</datatype>
<default>NULL</default></row>
<row name="level" null="1" autoincrement="0">
<datatype>INTEGER</datatype>
<default>NULL</default></row>
<row name="name" null="1" autoincrement="0">
<datatype>TEXT</datatype>
<default>NULL</default></row>
<row name="school" null="1" autoincrement="0">
<datatype>TEXT</datatype>
<default>NULL</default></row>
<row name="id_spells" null="1" autoincrement="0">
<datatype>TEXT</datatype>
<default>NULL</default></row>
<row name="casting_time" null="1" autoincrement="0">
<datatype>TEXT</datatype>
<default>NULL</default></row>
<row name="range" null="1" autoincrement="0">
<datatype>TEXT</datatype>
<default>NULL</default></row>
<row name="components" null="1" autoincrement="0">
<datatype>TEXT</datatype>
<default>NULL</default></row>
<row name="duration" null="1" autoincrement="0">
<datatype>TEXT</datatype>
<default>NULL</default></row>
<row name="description" null="1" autoincrement="0">
<datatype>TEXT</datatype>
<default>NULL</default></row>
<key type="PRIMARY" name="">
<part>id</part>
</key>
</table>
<table x="221" y="11" name="temp">
<row name="id" null="1" autoincrement="1">
<datatype>TEXT</datatype>
<default>NULL</default></row>
<row name="spell_id" null="1" autoincrement="0">
<datatype>TEXT</datatype>
<default>NULL</default><relation table="spells" row="id" />
</row>
<key type="PRIMARY" name="">
<part>id</part>
</key>
</table>
<table x="421" y="128" name="classes">
<row name="id" null="1" autoincrement="1">
<datatype>TEXT</datatype>
<default>NULL</default></row>
<row name="name" null="1" autoincrement="0">
<datatype>TEXT</datatype>
<default>NULL</default></row>
<key type="PRIMARY" name="">
<part>id</part>
</key>
</table>
<table x="208" y="124" name="class_spell_link">
<row name="id" null="0" autoincrement="1">
<datatype>INTEGER</datatype>
</row>
<row name="spell_id" null="1" autoincrement="0">
<datatype>TEXT</datatype>
<default>NULL</default><relation table="spells" row="id" />
</row>
<row name="class_id" null="1" autoincrement="0">
<datatype>INTEGER</datatype>
<default>NULL</default><relation table="classes" row="id" />
</row>
<key type="PRIMARY" name="">
<part>id</part>
</key>
</table>
</sql> -->
