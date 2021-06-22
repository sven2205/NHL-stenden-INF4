import string
import itertools
import sys


def main():
    if len(sys.argv) != 3:
        sys.exit('usage python genetic_linkage_map_constructor.py marker_subset.txt DegreesOfFreedom')
    global freedom_control
    freedom_control = int(sys.argv[2])
    if freedom_control == 0 or freedom_control >= 4:
        sys.exit('Degrees of freedom must be 1, 2 or 3')

    file = sys.argv[1]
    file_dictionary, total = read_file(file)
    data_dict = comparison(file_dictionary)
    score_dict = Rf_value(data_dict, total)
    group_distances, max_marker = distance(score_dict)
    write_mct(group_distances, max_marker)


def read_file(file):
    #prepare some dictionary and list
    marker = ""
    file_dictionary = {}
    data = []

    #Skip reading first 7 lines
    with open(sys.argv[1]) as file:
        for i in range(7):
            line = file.readline()

        for line in file:
            if line.startswith(tuple(string.ascii_letters)) or not line.strip():
                #if statement strips the marker name
                if marker:
                    #merged is a list = 'a', 'b', etc.
                    merged = list(itertools.chain.from_iterable(data))
                    if chi_squared(merged):
                        file_dictionary[marker] = merged
                    #store data
                    data = []
                if line.strip():
                    marker = line.split()[0]
            else:
                data.append(line.split())
        total = len(merged)
        file_dictionary[marker] = merged
    return file_dictionary, total


def chi_squared(merged):
    #calculate chi square
    a_count = merged.count("a")
    b_count = merged.count("b")
    expected_a = expected_b = len(merged) / 2

    chisq_a = ((a_count - expected_a) ** 2) / expected_a
    chisq_b = ((b_count - expected_b) ** 2) / expected_b
    p_value = chisq_a + chisq_b
    degrees_freedom = ["", 3.84, 5.99, 7.81]

    if p_value <= degrees_freedom[freedom_control]:
        return True
    else:
        return False


def comparison(file_dictionary):
    data_dict = {}
    for marker1 in range(len(file_dictionary.keys())):
        first_marker_list = list(file_dictionary.keys())
        #print(first_marker_list) = Names
        for marker2 in range(marker1+1, len(file_dictionary)):
            #print(marker2) = Number
            second_marker = first_marker_list[marker2]
            #print(second_marker) = Names
            amount = 0
            #compare markers with eachother
            for i in range(len(file_dictionary[first_marker_list[marker1]])):
                first_marker = first_marker_list[marker1]
                if file_dictionary[first_marker][i] == "-" or file_dictionary[second_marker][i] == "-":
                    continue
                elif file_dictionary[first_marker][i] != file_dictionary[second_marker][i]:
                    amount += 1
                key = str(first_marker) + "/" + str(second_marker)
            data_dict[key] = amount
            #print(data_dict[key]) = comparison numbers
    #print(marker1) = amount of markers
    return data_dict


def Rf_value(data_dict, total):
    #recombination factors
    score_dict = {}
    for markers, counts in data_dict.items():
        score_dict[markers] = (counts / total) * 100
    return(score_dict)


def distance(score_dict):
    group_distances = []
    #use of lambda to specify directly inline, return the second element that is larger than the previous element
    score_list = sorted(score_dict.items(), key = lambda
            item: item[1])
    #isolate markers in order
    max_marker = score_list[0][0].split("/")[0]
    #reserve a spot for potential second marker next to first marker
    sec_marker = ""
    #manually append the top of file and the first marker
    group_distances.append(("GROUP" + "/" + max_marker, 1))
    group_distances.append((max_marker + "/" + max_marker, 0.0))
    #if the second marker is next to first marker, manually insert it aswell to avoid bug
    if score_list[0][1] == 0.0:
        sec_marker = score_list[0][0].split("/")[1]
        group_distances.append((sec_marker + "/" + max_marker, 0.0))
    #finish the list with other markers
    for i in range(1, len(score_list)):
        if max_marker in score_list[i][0]:
            group_distances.append(score_list[i])

    print("Markers:", len(group_distances) - 1)
    #semi bug
    """print(group_distances)"""
    return group_distances, max_marker


def write_mct(group_distances, max_marker):
    #write a .mct file which is the correct extension type for MapChart so it can read the file
    #clean list to put markers in
    markers_list = []
    for i in range(len(group_distances)):
        #split markers and distances
        markers = group_distances[i][0].split(",")[0]
        #seperate the max_marker from the useable markers
        marker_split = markers.split("/")
        #fill the list with clean markers
        markers_list.append(marker_split[0])

    #open a new file
    with open('group_distances.mct', 'w') as output_file:
        for i in range(len(markers_list)):
            #write the marker + some room + distance
            #str is not necessary for the marker list but it is for code aesthetics
            output_file.write(str(markers_list[i])+"\t")
            output_file.write(str(group_distances[i][1]))
            output_file.write("\n")
    print("Linkage map complete!")

main()