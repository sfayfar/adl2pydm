def parse(displayInfo, offset):
    """
    parse MEDM XXXooREPLACEooXXX block
    """
    global block_number
    medm_widget = MEDM_Widget("WIDGETTAG", "WIDGETNAME", block_number)
    block_number += 1

    nestingLevel = 0

    while True:
        if veryFirst:
            tokenType, token = firstTokenType, firstToken
        else:
            tokenType, token = getToken(displayInfo)

        if tokenType == T_WORD:
            getNextElement(displayInfo, token, offset)
        
        elif tokenType == T_EQUAL:
            pass
        
        elif tokenType == T_LEFT_BRACE:
            nestingLevel += 1
        
        elif tokenType == T_RIGHT_BRACE:
            nestingLevel -= 1
 
        if tokenType in (T_RIGHT_BRACE, T_EOF) or nestingLevel == 0:
            break
    
    if not QT_OUTPUT:
        print(str(medm_widget))
    return tokenType
