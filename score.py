class ScoreCalculator:

    def calculate_score(self, cpu, gpu, purpose):

        if purpose == "game":
            return cpu.game_score * 0.3 + gpu.game_score * 0.7

        elif purpose == "work":
            return cpu.work_score * 0.7 + gpu.work_score * 0.3

        elif purpose == "ai":
            return cpu.work_score * 0.2 + gpu.ai_score * 0.8
   

    def calculate_balance_score(self, cpu, gpu):

        ratio = cpu.price / gpu.price

        ideal = 0.5

        score = 100 - abs(ratio-ideal)*100

        return max(0, min(score,100))
        
    def calculate_value_score(self, cpu, gpu):

        return (
            cpu.value_score +
            gpu.value_score
    ) / 2
    
    def calculate_final_score(self, cpu, gpu, purpose):

        performance = self.calculate_score(cpu, gpu, purpose)

        balance = self.calculate_balance_score(cpu, gpu)

        value = self.calculate_value_score(cpu, gpu)

        if purpose == "game":
            final = performance*0.6 + balance*0.2 + value*0.2

        elif purpose == "work":
            final = performance*0.5 + balance*0.1 + value*0.4

        elif purpose == "ai":
            final = performance*0.7 + balance*0.1 + value*0.2
        
        return final