import random
import uuid
import pandas as pd
from datetime import datetime


class Client:
    data = {200: [0.15, 0.61], 250: [0.12, 0.59], 300: [0.12, 0.48], 400: [0.12, 0.37], 500: [0.12, 0.29],
            600: [0.12, 0.27], 700: [0.11, 0.2], 800: [0.07, 0.18], 900: [0.05, 0.17], 1000: [0.02, 0.12]}

    def __init__(self):
        self.name = uuid.uuid1()
        self.score_band = None
        self.default = None

    def __str__(self):
        return f"client {self.name}"

    def scoring(self):
        keys = list(Client.data.keys())
        probs = [i[0] for i in list(Client.data.values())]
        self.score_band = random.choices(population=keys, weights=probs)[0]
        self.default = random.choices(population=[True, False], weights=[Client.data[self.score_band][1],
                                                                    1- Client.data[self.score_band][1]])[0]


    def make_application(self):
        self.scoring()
        return Application(name=self.name, score=self.score_band, default=self.default)

class Application:
    """distribution of haw many days customers use the loan"""
    term_data = {3: 0.005050001, 4: 0.052365789, 5: 0.052365789, 6: 0.052365789, 7: 0.052365789, 8: 0.052365789,
                 9: 0.052365789, 10: 0.052365789, 11: 0.052365789, 12: 0.052365789, 13: 0.052365789, 14: 0.052365789,
                 15: 0.052365789, 16: 0.052365789, 17: 0.052365789, 18: 0.052365789, 19: 0.052365789, 20: 0.052365789,
                 21: 0.052365789, 22: 0.052365789}
    """distribution of ticket granted"""
    ticket_data = {1000: 0.015350747, 1100: 0.004837529, 1200: 0.005812795, 1300: 0.01137466, 1400: 0.007737459,
                   1500: 0.015754305, 1600: 0.008182408, 1700: 0.007509811, 1800: 0.025178432, 1900: 0.006811344,
                   2000: 0.006945864, 2100: 0.004928071, 2200: 0.343643047, 2300: 0.022286263, 2400: 0.009093002,
                   2500: 0.007320966, 2600: 0.008112562, 2700: 0.006423307, 2800: 0.027354027, 2900: 0.014898037,
                   3000: 0.007256293, 3100: 0.006425894, 3200: 0.008081519, 3300: 0.011224619, 3400: 0.005986119,
                   3500: 0.006534544, 3600: 0.008963656, 3700: 0.019792478, 3800: 0.366180241}
    """distribution of approval rate depending on score"""
    approve_data = {200: 0.05, 250: 0.1, 300: 0.16, 400: 0.23, 500: 0.45, 600: 0.55, 700: 0.65,
                     800: 0.7, 900: 0.75, 1000: 0.9}

    def __init__(self, name, score: float, default: bool):
        """creates an instance of application"""
        self.name = name
        self.created_at = datetime.now()
        self.rate = 0.09589041
        self.term = None
        self.ticket = None
        self.score = score
        self.approved = None
        self.accepted = None
        self.default = default

    def get_approve(self):
        self.approved = random.choices(population=[True, False], weights=[Application.approve_data[self.score],
                                                                          1- Application.approve_data[self.score]])[0]
    def get_term(self):
        keys = list(Application.term_data.keys())
        probs = list(Application.term_data.values())
        self.term = random.choices(population=keys, weights=probs)[0]

    def get_ticket(self):
        keys = list(Application.ticket_data.keys())
        probs = list(Application.ticket_data.values())
        self.ticket = random.choices(population=keys, weights=probs)[0]

    def get_accepted(self):
        if self.approved:
            accept_rate = random.triangular(low=0.6, high=0.9, mode=0.77)
            self.accepted = random.choices(population=[True, False], weights=[accept_rate, 1 - accept_rate])[0]


class Portfolio:
    def __init__(self, days):
        self.days = days
        """number of deals issued"""
        self.portfolio = pd.DataFrame(0, index=[i for i in range(1, self.days + 1)],
                                      columns=[i for i in range(1, self.days + 1)])
        """amount issued"""
        self.issuance = self.portfolio.copy()
        """principal repaid"""
        self.repayment = self.portfolio.copy()
        """interest charged"""
        self.interest = self.portfolio.copy()

    def add_deal(self, deal, issue_day):
        for name in self.portfolio.columns:
            if issue_day <= name <=deal.term + issue_day:
                self.portfolio.loc[issue_day, name] = self.portfolio.loc[issue_day, name] + 1

    def issue_credit(self, deal, issue_day):
        for name in self.issuance.columns:
            if issue_day == name:
                self.issuance.loc[issue_day, name] = self.issuance.loc[issue_day, name] + deal.ticket * -1

    def charge_interest(self, deal, issue_day):
        if not deal.default:
            for name in self.interest.columns:
                if issue_day <= name <= deal.term + issue_day:
                    self.interest.loc[issue_day, name] = self.interest.loc[issue_day, name] + deal.ticket * deal.rate

    def repay_principal(self, deal, issue_day):
        if not deal.default:
            for name in self.repayment.columns:
                if name == deal.term + issue_day:
                    self.repayment.loc[issue_day, name] = self.repayment.loc[issue_day, name] + deal.ticket

    def save_it_all(self):
        filename = 'portfolio.xlsx'
        with  pd.ExcelWriter(filename, engine='openpyxl') as writer:
            self.portfolio.to_excel(writer, sheet_name='deals')
            self.issuance.to_excel(writer, sheet_name='loans')
            self.interest.to_excel(writer, sheet_name='interest')
            self.repayment.to_excel(writer, sheet_name='repayments')

days_to_model = 365
my_portfolio = Portfolio(days=days_to_model)
for day in range(1, days_to_model + 1):
    demand = int(random.triangular(low=2_000, mode=3_000, high=4_000))
    for lead in range(0, demand):
        client = Client()
        application = client.make_application()
        application.get_approve()
        if application.approved:
            application.get_term()
            application.get_ticket()
            application.get_accepted()
            if application.accepted:
                my_portfolio.add_deal(deal=application, issue_day=day)
                my_portfolio.issue_credit(deal=application, issue_day=day)
                my_portfolio.charge_interest(deal=application, issue_day=day)
                my_portfolio.repay_principal(deal=application, issue_day=day)
my_portfolio.save_it_all()
