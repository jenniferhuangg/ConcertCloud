import prompts

class AIwrapper:
    def __init__(self, model="mistral")
        self.model = model
        self.apiurl = "http://localhost:11434/api/generate"

    def ask(self, prompt):
        response = requests.post(self.apiurl, json={
            "model": self.model,
            "prompt": prompt, 
            "stream": False
        })
        data = response.json()
        return data.get("response","No returned response")
    except Exeception as err:
        return f"Error: {str(err)}"