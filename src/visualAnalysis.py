import pandas as pd


class VisualAnalysis:
    def __init__(self):
        pass

    def showTerminal(self, gamedata):
        print(gamedata)
        inaccuracy = 80
        mistake = 120
        blunder=180
        lost = 450
        ok = 50
        great = 25
        excellent = 10
        best = 1
        moves = pd.DataFrame(columns=['Ply', 'Side', 'Move', 'CP', 'CP Delta', 'Type', 'Suggested', 'Depth'])
        move_list = []
        for index, row in gamedata.iterrows():
            move_type = None
            if row['Side'] == "B":
                if row['CP Delta'] > lost:
                    move_type = 'Lost'
                elif row['CP Delta'] > blunder:
                    move_type = 'Blunder'
                elif row['CP Delta'] > mistake:
                    move_type = 'Mistake'
                elif row['CP Delta'] > inaccuracy:
                    move_type = 'Inaccuracy'
                elif row['CP Delta'] <= best:
                    move_type = 'Best Move'
                elif row['CP Delta'] <= excellent:
                    move_type = 'Excellent'
                elif row['CP Delta'] <= great:
                    move_type = 'Great'
                elif row['CP Delta'] <= ok:
                    move_type = 'Good'
                else:
                    move_type = 'Ok'
            else:
                if row['CP Delta'] < -lost:
                    move_type = 'Lost'
                elif row['CP Delta'] < -blunder:
                    move_type = 'Blunder'
                elif row['CP Delta'] < -mistake:
                    move_type = 'Mistake'
                elif row['CP Delta'] < -inaccuracy:
                    move_type = 'Inaccuracy'
                elif row['CP Delta'] >= -best:
                    move_type = 'Best Move'
                elif row['CP Delta'] >= -excellent:
                    move_type = 'Excellent'
                elif row['CP Delta'] >= -great:
                    move_type = 'Great'
                elif row['CP Delta'] >= -ok:
                    move_type = 'Good'
                else:
                    move_type = 'Ok'
            if not move_type:
                move_type = "Lascou"
            move_list.append((row['Ply'], row['Side'], row['Move'], row['CP'], row['CP Delta'], move_type, row['Suggested'], row['Depth']))
        moves = pd.DataFrame(move_list, columns=['Ply', 'Side', 'Move', 'CP', 'CP Delta', 'Type', 'Suggested', 'Depth'])
        pd.options.display.max_rows = 1000
        self.finalResultTerminal(gamedata, moves)


    def finalResultTerminal(self,gamedata, moves):
        grt = -2
        ecl = -1
        ok = -4
        isc = -7
        msc = -12
        bsc = -24

        whitegreat = 0
        whiteok = 0
        whiteexcellent = 0
        whiteinaccuracies = 0
        whitemistakes = 0
        whiteblunders = 0

        blackgreat = 0
        blackok = 0
        blackexcellent = 0
        blackinaccuracies = 0
        blackmistakes = 0
        blackblunders = 0

        totalwhite = len(gamedata[gamedata['Side']== "W"])*10
        totalwhitescore = totalwhite
        totalblack = len(gamedata[gamedata['Side']== "B"])*10
        totalblackscore = totalblack

        for index,row in moves.iterrows():
            if row['Side'] == "B":
                if row['Type'] == "Inaccuracy":
                    totalblackscore += isc
                    blackinaccuracies +=1
                elif row['Type'] == "Mistake":
                    totalblackscore += msc
                    blackmistakes +=1
                elif row['Type'] == "Blunder":
                    totalblackscore += bsc
                    blackblunders +=1
                elif row['Type'] == "Ok":
                    totalblackscore += ok
                    blackok +=1
                elif row['Type'] == "Great":
                    totalblackscore += grt
                    blackgreat +=1
                elif row['Type'] == "Excellent":
                    totalblackscore += ecl
                    blackexcellent +=1
                elif row['Type'] == "Lost":
                    print("fail white")
            
            if row['Side'] == "W":
                if row['Type'] == "Inaccuracy":
                    totalwhitescore += isc
                    whiteinaccuracies +=1
                elif row['Type'] == "Mistake":
                    totalwhitescore += msc
                    whitemistakes +=1
                elif row['Type'] == "Blunder":
                    totalwhitescore += bsc
                    whiteblunders +=1
                elif row['Type'] == "Ok":
                    totalwhitescore += ok
                    whiteok +=1
                elif row['Type'] == "Great":
                    totalwhitescore += grt
                    whitegreat +=1
                elif row['Type'] == "Excellent":
                    totalwhitescore += ecl
                    whiteexcellent +=1
                elif row['Type'] == "Lost":
                    print("fail black")
                    
        whitequality = float(totalwhitescore)/float(totalwhite)
        blackquality = float(totalblackscore)/float(totalblack)            
        '''
        print("Event:",metaDataGame.event)
        print("Site:",metaDataGame.site)
        print("Date:",metaDataGame.date)
        print("Round:",metaDataGame.round)
        print("White:",metaDataGame.white)
        print("Black:",metaDataGame.black)
        print("Result:",metaDataGame.result)
        '''
        print("="*60)
        print("Quality of White Play:",round(whitequality*100,0),"%")
        print("White made ",whiteok,"Ok moves,",whiteexcellent,"Excellent moves", whitegreat,"Great Moves")
        print("White made",whiteinaccuracies,"inaccuracies,",whitemistakes,"mistakes, and", whiteblunders,"blunders.")
        print("="*60)
        print("Quality of Black Play:",round(blackquality*100,0),"%")
        print("Black made ",blackok,"Ok moves,",blackexcellent,"Excellent moves", blackgreat,"Great Moves")
        print("Black made",blackinaccuracies,"inaccuracies,",blackmistakes,"mistakes, and", blackblunders,"blunders.")

        