from modules.Evolution import Evolution

class Page(Evolution):
    '''
    Class will extend evolution class for printing functions
    '''

    def writeHTMLPage(self, simName, descr, degreeDistrib, creditDistr, numAuths='N/A', numPaps='N/A', numTops='N/A', numTypes='N/A', 
                        Pn='N/A', Pw='N/A', Pd='N/A', numRuns='N/A', directory='./'):
        '''
        Assumes all the files should be located in the same directory

        directory must end with '/'
        '''
        descrPlotsFile = f'{simName}Plots.png'
        degPlotsFile = f'{simName}Deg.png'
        creditPlotsFile = f'{simName}Credit.png'
        htmlfileName = directory + f'{simName}Page.html'

        # plot distributions
        self.plotDescriptorsDistr(saveToFile=directory + descrPlotsFile, ylogBase=10, xlogBase=10, data=descr, 
                                        numAuthors=numAuths, numPapers=numPaps, numTopics=numTops)
        self.plotDegreeDistr(degreeDistrib=degreeDistrib,saveToFile=directory + degPlotsFile)
        self.plotCreditDistr(creditDistr, saveToFile=directory + creditPlotsFile)

        with open(htmlfileName, 'w') as fileObj:
            fileObj.write(self.generateHTML(simName=simName, descrPlotFile=descrPlotsFile, degreePlotFile=degPlotsFile, creditPlotFile=creditPlotsFile,
                        numPapers=numPaps, numAuthors=numAuths, numTopics=numTops, numTypes=numTypes, Pn=Pn, Pw=Pw, Pd=Pd, numRuns=numRuns))
        print(f'Saved to {htmlfileName} successfully!')

    def generateHTML(self, simName, descrPlotFile, degreePlotFile, creditPlotFile, numPapers='N/A', numAuthors='N/A', numTopics='N/A', numTypes='N/A',
                        Pn='N/A', Pw='N/A', Pd='N/A', numRuns='N/A',):

        return f'''

        <!DOCTYPE html>
        <html>
            <head>
            <title>{simName}</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
            <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Raleway">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
            <style>
                body,h1 {{font-family: Arial, sans-serif}}
                h1 {{letter-spacing: 6px}}
                .w3-row-padding img {{margin-bottom: 12px}}
                #parameters {{
                    font-family: Arial, Helvetica, sans-serif;
                    border-collapse: collapse;
                    width: auto;
                    margin-left: auto; 
                    margin-right: auto;
                    margin-bottom: 50px;
                }}
                #parameters td, #parameters th {{
                    border: 1px solid #ddd;
                    padding: 8px;
                }}
                #parameters tr:nth-child(even){{background-color: #f2f2f2;}}
                #parameters tr:hover {{background-color: #ddd;}}
                #parameters th {{
                    padding-top: 12px;
                    padding-bottom: 12px;
                    text-align: left;
                    background-color: #04AA6D;
                    color: white;
                }}
            </style>
            </head>

            <body>
            <!-- !PAGE CONTENT! -->
            <div class="w3-content" style="max-width:1500px">

            <!-- Header -->
            <header class="w3-panel w3-center w3-padding-32 w3-light-grey">
                <h1 class="w3-xlarge">Simulation outputs for {simName} </h1>
            </header>

            <!-- Chart Grid -->
            <div class="w3-row-padding" style="margin-bottom:128px">
                <div class="w3-half">
                    <!-- Parameter Table -->
                    <table id="parameters">
                        <tr>
                            <th>Parameter</th>
                            <th>Value</th>
                        </tr>
                        <tr>
                            <td>Number of Averaged Trials</td>
                            <td>{numRuns}</td>
                        </tr>
                        <tr>
                            <td>Pn</td>
                            <td>{Pn}</td>
                        </tr>
                        <tr>
                            <td>Pw</td>
                            <td>{Pw}</td>
                        </tr>
                        <tr>
                            <td>Pd</td>
                            <td>{Pd}</td>
                        </tr>
                    </table>
                    <img src={descrPlotFile} style="width:100%">
                </div>

                <div class="w3-half">
                    <!-- Parameter Table -->
                    <table id="parameters">
                        <tr>
                            <th>Measure</th>
                            <th>Value</th>
                        </tr>
                        <tr>
                            <td>Number of Papers</td>
                            <td>{numPapers}</td>
                        </tr>
                        <tr>
                            <td>Number of Authors</td>
                            <td>{numAuthors}</td>
                        </tr>
                        <tr>
                            <td>Number of Topics</td>
                            <td>{numTopics}</td>
                        </tr>
                        <tr>
                            <td>Number of Types</td>
                            <td>{numTypes}</td>
                        </tr>
                    </table>
                    <img src={degreePlotFile} style="width:100%">
                    <img src={creditPlotFile} style="width:100%">
                </div>
            </div>
            
            <!-- End Page Content -->
            </div>

            <!-- Footer -->
            <footer class="w3-container w3-padding-64 w3-light-grey w3-center w3-large"> 
                <i class="fa fa-facebook-official w3-hover-opacity"></i>
                <i class="fa fa-instagram w3-hover-opacity"></i>
                <i class="fa fa-snapchat w3-hover-opacity"></i>
                <i class="fa fa-pinterest-p w3-hover-opacity"></i>
                <i class="fa fa-twitter w3-hover-opacity"></i>
                <i class="fa fa-linkedin w3-hover-opacity"></i>
                <p>Powered by <a href="https://www.w3schools.com/w3css/default.asp" target="_blank" class="w3-hover-text-green">w3.css</a></p>
            </footer>

        </body>
        </html>
        '''