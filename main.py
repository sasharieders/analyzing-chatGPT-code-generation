from cProgramGenerator import CProgramGenerator
from SOSumAnaly import preprocessSosum
from SOSumAnaly import summaryComp

#Since it takes a long time to generate the code and the API crashes sometimes, I just uploaded the folders with the programs here but you can see in cProgramGenerator.py how I got them
def main():
    userInp = input("What would you like to do?\n1. Test a folder containing C programs.\n2. Load in the SOSum dataset and compare its summaries to chatGPT generated summaries.\nChoose an option (1 or 2): ")
    if userInp == '1':
        folderPath = input("Please enter the path to the folder containing the C programs: ")
        #this is here for if you want to generate the c programs using chatGPT 
        apiKey = input("Please enter your API Key:\n")
        prompt = ""
        generator = CProgramGenerator(apiKey,prompt)
        totalNumProgs,numSuccessPrograms = generator.testGeneratedCode(folderPath)
        print("Number of programs tested: ", totalNumProgs)
        print("Number of successfully executed programs:", numSuccessPrograms)

    else:
        preprocessor = preprocessSosum()




if __name__ == "__main__":
    main()