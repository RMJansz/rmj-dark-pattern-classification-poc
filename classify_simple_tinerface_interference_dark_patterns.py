def classify_simple_interface_interference_patterns(elements):
    acceptButton = None
    declineButton = None
    optionsButton = None
    
    for element in elements:
        if element[3] == 1:
            acceptButton = element
        if element[3] == 2:
            declineButton = element
        if element[3] == 3:
            optionsButton = element
        
    if acceptButton is None and declineButton is None and optionsButton is None:
        print('Possibly no cookie dialog dark pattern')
    if acceptButton is not None and declineButton is not None:
        acceptButtonArea = acceptButton[13] * acceptButton[14]
        declineButtonArea = declineButton[13] * declineButton[14]
        if acceptButtonArea != declineButtonArea:
            print('Button size mismatch')
    print(elements)