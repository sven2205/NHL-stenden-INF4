# Genetic linkage map constructor
#### Video Demo:  <https://youtu.be/22-1GrwVZ4A>
## Description:

## Background info of the general overview of molecular plant biology
My project consists of a python program that takes *raw* marker data and turns it into a usable genetic linkage map.
The necessity for this program lays in the fact that plants are of vital importance; they provide us with food, oxygen,
building materials, clothing and fuel. Without plants, our lives would be impossible. Since the early stage of
agriculture, around 12000 years ago,we have altered some of these plants through a process called domestication,
which improves our own food production.

#### Not needed for explaination
~~Plant breeding is done by making deliberate crosses and subsequent selection. Breeding plants started only 100 years
ago and has improved our crops even further, so that they are easy to grow, harvest and provide a higher yield.
In the last ten years there has been an uprise in molecular biology, genomics and bio-informatics which provides
new opportunities to study plant processes and improve crops. This uprising is needed to be able to feed everyone
in the future. The improvement of crops is highly demanded, since our food production is threatened by the decrease
of farmland due to the growing human population, imminent climate change and many plant diseases that destroy our crops.
To ensure our food production in the future, we need crops that can grow more efficiently, have a higher
nutritional value and are resistant to a variety of biotic and abiotic stress factors.

Biodiscovery is a hot topic that encompasses the search for new crops, the improvement of crops and the search
for new secondary metabolites in plants. Modern molecular techniques, such as Next Generation Sequencing,
produce a huge amount of data. Bio-informatics is a tool in biology to give some order in this chaos.
Being able to perform data mining in molecular databases is a necessary skill for biologists. Using molecular tools,
like amplifying, sequencing and aligning certain parts of a genome will give us information on
evolutionary relationships. Nowadays, much more genetic information is available like for example
gene sequence and function or gene and QTL positions on genetic linkage maps along with physical maps for all
model crops and many other crops.~~

## Program explaination
The program Genetic linkage map constructor.py has to be run with specific parameters which consist of the raw data file
and the degrees of freedom. The degree of freedom is stored in a global value for later use in the program.
Sys arguments are used to check whether the correct parameters are given when launching the program. When the program
loads the raw data from the raw data file; marker subset.txt it will read it from line 8 onwards as stated in the
defined **read_file**. The file is read and the raw data is sorted and stored in a dictionary. Building genetic linkage
maps is a statistical process so the chi-squared has to be calculated for every marker. The chi-squared is calculated
by calculating the expected value of 'a' and 'b' in the entire marker set and then using the 'a' and 'b' from each
marker individually. If the chi-squared falls outside the maximum deviation, set by the amount of degrees of freedom,
the marker is removed from the dictionary.

The second step is comparing differences in the markers with each other, this is done in the **comparison** defined.
It takes each marker individually and compares it against the rest until all markers have been compared with each other.
You could say that it is some sort of algorithm. The scores for each comparison is stored in a dictionary and thereafter
used in the **Rf_value** defined to calculate the recombination factor for each comparison. The Rf value is quite easily
calculated by taking the score from the comparison and divide it with the total length of the marker times 100, the
Rf values are then stored in a dictionary. The final step in the calculation process consists of calculating the
distance between the markers. This is done in the **distance** defined, here the dictionary from the last step is
sorted by ascending score and placed in a list. The marker that has the lowest score is isolated and manually
injected into a new list. At the same time there is a check if the second marker is directly next to the first marker,
if this is the case the second marker is also manually inserted into the list. To top the function of, the rest of the
markers are then automatically inserted into the list.

Finally the list is split a few times to prepare it for writing to the output file. The output file is created as a
.mct file extension so that mapchart ("Wageningen University" (software that is used to display the file)) can read
the file directly and that there is no need for manual conversion. The marker names and distances are alternately
written to the output file. To top it all of a Linkage map complete! phrase is printed in the terminal to alert the
user of its completion. And that's it! the output file is correctly formatted and can now directly be read by mapchart.
