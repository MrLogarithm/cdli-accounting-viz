# CDLI Commodity Visualization
## User Guide

# 1. Introduction
This is the user guide for the commodity visualizations in `framework/app/tools/commodity-viz/`. Technical documentation is available [here](https://gitlab.com/cdli/framework/-/blob/phoenix/feature/commodities/app/tools/commodity-viz/README.md).

These visualizations are intended to help users explore how various goods are represented in the ancient economy. Using these tools, users are able to discover how frequently a given item is recorded in ancient accounting texts, how often groups of items occur together, what varieties or subtypes of an item have been recorded, and more.

The data used for these visualizations has been extracted using automated tools built around [wordnet](https://wordnet.princeton.edu/) and the [ePSD](http://psd.museum.upenn.edu/nepsd-frame.html). The extracted data has been examined by human experts, but as with all automated tools some mistakes will exist. Most often these arise from variant spellings, unclear or missing definitions, or ambiguous numeric notations. Known issues are tracked on [gitlab](https://gitlab.com/cdli/framework/-/issues), and we welcome additional corrections.

# 2. Corpus Selection
At present, there is no way to select a corpus directly from the visualization page. This will change in a future release. 

The easiest way to specify a corpus is to use the CDLI search page to find texts of interest, and follow the link from the search results to this visualization. 

It is also possible to specify a corpus using the `corpus` URL parameter. For example, http://127.0.0.1/cdli-accounting-viz/?corpus=P100839+P104809+P221487+P221495 will visualize the data in texts P100839, P104809, P221487 and P221495.

# 3. Visualization Modules

## 3.1. Searching and Filtering
Type a Sumerian word into the search bar and press Enter to focus that word in the visualization. As you type, an autocomplete menu will show words matching what you have entered so far. Our data combines information from multiple transliterators as well as the ePSD, so some words may be attested with multiple spellings. If your search term does not seem to exist, consult the autocomplete suggestions to see if an alternate spelling has been used.

<img src='https://gitlab.com/cdli/framework/-/raw/phoenix/feature/commodities/app/tools/commodity-viz/docs/img/autocomplete.gif' />

Once you enter a search term, the radio buttons beside the search bar will show the different number systems used to count that object. Click the radio buttons to switch between different uses of your search term. Note that many Sumerian numeral notations are ambiguous, and could potentially belong to any of several counting systems. We have tried to disambiguate these cases, but there is the possibility that some counts may have been assigned to the wrong system.

Whenever a commodity word occurs on the page, you can click on it to refocus the visualization. The word you clicked on will become the new search term and the figures will be redrawn.

## 3.1. Histogram and Summary Statistics
This module gives an overview of the numeric values associated with your search term. 

<img src='https://gitlab.com/cdli/framework/-/raw/phoenix/feature/commodities/app/tools/commodity-viz/docs/img/histogram-tooltip.gif' />

The histogram shows the item's overall distribution. Hovering over a bar on the histogram will show a tooltip telling you exactly how often numbers in a certain range are used to count the search term. The slider to the side of the histogram lets you control the granularity of the figure.

<img src='https://gitlab.com/cdli/framework/-/raw/phoenix/feature/commodities/app/tools/commodity-viz/docs/img/histogram-slider.gif' />

Immediately below the histogram, you will see how many entries in the corpus record your chosen item, and how many of the item are recorded in sum.

<img src='https://gitlab.com/cdli/framework/-/raw/phoenix/feature/commodities/app/tools/commodity-viz/docs/img/stats.jpg' />

The bottom part of this module summarizes basic statistics about the item's distribution, such as the average value, the most common value, and how much variation there is in the attested values.

## 3.2. Concordance
The concordance module shows all of the entries in the corpus which contain your search term as a counted object. The Value column gives the value of the count in arabic notation, and the Occurrences column shows how many times this line occurs in the corpus. Click on the column names to sort the table. 

If you hover over a value in the Occurrences column, a tooltip will show which texts contain the associated line. Clicking on the value will open a CDLI search result showing these texts in transliteration.

<img src='https://gitlab.com/cdli/framework/-/raw/phoenix/feature/commodities/app/tools/commodity-viz/docs/img/concordance-tooltip.gif' />

You can type into the Filter bar at the top of the Concordance module to search for lines which contain a certain word or phrase.

## 3.3 Nearby Items
### 3.3.1. Table View
This table lists the other counted objects which occur in documents containing your search term. In each row, the first column shows a counted object, and the second column counts how many texts contain both that object and your search term. 

<img src='https://gitlab.com/cdli/framework/-/raw/phoenix/feature/commodities/app/tools/commodity-viz/docs/img/nearby-tooltip.gif' />

Hovering over a value in the Occurrences column will list the texts that contain both words, and clicking on the value will take you to a CDLI search containing those texts. As in the Concordance module, you can use the Filter bar to search for rows containing a particular word.

### 3.3.2. Graph View
Click the toggle in the corner of the module to switch to the graph view. In addition to showing the items which occur with your search term, this view shows how often these items occur with one another. 

Each node in the graph is an item which occurs in texts containing your search term. Two items are connected by an edge if they also occur in texts together, and thicker edges denote more frequent co-occurrence. Hovering over a node will highlight all of the other nodes which are connected to it, which helps in interpreting dense graphs.

Strongly connected components tend to represent different "genres" of text that your item can occur in. Sometimes, these components can be easily seen, as in the figure below which has two distinct clouds of items. 

<img src='https://gitlab.com/cdli/framework/-/raw/phoenix/feature/commodities/app/tools/commodity-viz/docs/img/connected-components.jpg' />

If the figure is dense and connected components are hard to identify, clicking the "Highlight Cliques" button will make them light up when you hover your mouse over the graph.

<img src='https://gitlab.com/cdli/framework/-/raw/phoenix/feature/commodities/app/tools/commodity-viz/docs/img/clique-1.gif' />
<img src='https://gitlab.com/cdli/framework/-/raw/phoenix/feature/commodities/app/tools/commodity-viz/docs/img/clique-2.gif' />

The sliders in the corner of the figure control how many items are displayed. The top slider controls how rare a word can be before it is pruned from the figure: at the left extreme, only the most common items are included in the figure, and at the right extreme all words are included. The second slider controls how many connections are included. At the left extreme, nodes are only connected if they occur together frequently. At the right extreme nodes may be connected even if they only occur in a single text together. Nodes with no connected edges are pruned from the figure, so this slider will adjust the overall number of nodes and not just the edge density.

To zoom, scroll the mouse wheel or double-click the figure. Click and drag the background to pan, or click and drag a node to untangle dense clusters of nodes.

## 3.4. Descriptors
### 3.3.1. Table View
This table shows the adjectives and other modifiers which can be used to describe your search term. The first column shows the search term with an adjective or other modifier, and the second column counts how many lines contain that phrase. Hover over the count to see a list of texts which contain the associated phrase, or click the count to see those texts in full. Use the Filter bar to search for rows containing a particular word.

### 3.3.2. Graph View
The graph view shows which descriptors can be used together. Each node is a descriptor which can be applied to your search term, and two words are connected by an edge if they are both used to describe the same instance of your search term. This can reveal different uses of the item in question.

For example, the figure below shows modifiers associated with *masz* "goat". We see that goats are sometimes described as both "babbar2" and "bar-dul5" (white and used for garment production), and sometimes as "gu7" and "sze" (fed a diet of barley). But there is no link between "sze" and "bar-dul5", implying that when an animal was used for garment production its diet was not recorded.

<img src='https://gitlab.com/cdli/framework/-/raw/phoenix/feature/commodities/app/tools/commodity-viz/docs/img/descriptors.jpg' />

Consult the section on the Nearby Items graph view for an explanation of the figure parameters. 

<img src='https://gitlab.com/cdli/framework/-/raw/phoenix/feature/commodities/app/tools/commodity-viz/docs/img/descriptors-slider.gif' />


## 3.5. Similar Items
This module displays items which have a similar distribution to your search term. There are two views: in the reduced view, the histogram displays the difference between your search term's distribution and the distribution of other counted objects. The height of the bar shows how much more or less frequently a given range of values occur with the listed item than with your search term. If all of the bars are short, the items have nearly identical distributions. Pay careful attention to the scale of the vertical axis: bars that look tall may represent small differences. You can hover over a bar to see a tooltip giving the exact difference.

<img src='https://gitlab.com/cdli/framework/-/raw/phoenix/feature/commodities/app/tools/commodity-viz/docs/img/similar-reduced-tooltip.gif' />

Click the toggle in the corner of the module to switch to the full view. In this view, the object's full distribution is shown as a histogram, which may be compared to the Histogram module described above. 

<img src='https://gitlab.com/cdli/framework/-/raw/phoenix/feature/commodities/app/tools/commodity-viz/docs/img/similar-full.gif' />

## 3.6. Other

In the top left corner you will find the Help, Random Word, and Cite buttons. 

<img src='https://gitlab.com/cdli/framework/-/raw/phoenix/feature/commodities/app/tools/commodity-viz/docs/img/other-buttons.jpg' />

The Help button will reopen the welcome modal which describes the page and links to this guide.

The Random Word button will search for a random word, for users interested in exploratory visualization.

The Cite button will open a modal which allows you to export a citation for these visualizations. The link in the citation will include your current search term and all of your current parameter settings, allowing you to share the visualizations in exactly the state the appear to you at the time of export. 

# 4. API Access
The API can be queried directly at http://127.0.0.1:8087/. Please consult the API documentation at http://127.0.0.1:8087/docs/ for additional details.

