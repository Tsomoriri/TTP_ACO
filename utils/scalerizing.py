def profit_with_renting_ratio(self, profit, time):
        # caculate profit with renting ratio
        return profit - self.info['RENTING_RATIO'] * time
    
    
def scale1(self, profit, time):
        # caculate profit with renting ratio
        w2 = self.info['RENTING_RATIO']/self.w1
        return self.w1*profit + math.log(w2/time)
    
def scale2(self, profit, time):
        # caculate profit with renting ratio
        w2 = self.info['RENTING_RATIO']/self.w1
        return self.w1*profit + math.exp(-w2*time)