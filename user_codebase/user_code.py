def find_common_elements(list1, list2, list3):
    common = []
    for item in list1:
        found_in_2 = False
        for item2 in list2:
            if item == item2:
                found_in_2 = True
                break
        
        if found_in_2:
            found_in_3 = False
            for item3 in list3:
                if item == item3:
                    found_in_3 = True
                    break
            
            if found_in_3 and item not in common:
                common.append(item)
    
    return common