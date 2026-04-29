# { "Depends": "py-genlayer:test" }

from genlayer import *

STATUS_OPEN = "open"
STATUS_IN_PROGRESS = "in_progress"
STATUS_SUBMITTED = "submitted"
STATUS_COMPLETED = "completed"
STATUS_DISPUTED = "disputed"


class FreelanceEscrow(gl.Contract):

    client: Address
    freelancer: Address
    payment_amount: u256

    job_title: str
    job_description: str
    acceptance_criteria: str

    proof_of_work: str
    status: str

    ai_verdict: str
    ai_reasoning: str


    def __init__(self, job_title: str, job_description: str, acceptance_criteria: str):

        self.client = gl.message.sender_address
        self.freelancer = gl.message.sender_address
        self.payment_amount = gl.message.value

        self.job_title = job_title
        self.job_description = job_description
        self.acceptance_criteria = acceptance_criteria

        self.proof_of_work = ""
        self.status = STATUS_OPEN

        self.ai_verdict = ""
        self.ai_reasoning = ""


    @gl.public.write
    def accept_job(self):
        assert self.status == STATUS_OPEN, "Job not open"
        self.freelancer = gl.message.sender_address
        self.status = STATUS_IN_PROGRESS


    @gl.public.write
    def submit_work(self, proof: str):
        assert self.status == STATUS_IN_PROGRESS, "Not in progress"
        assert len(proof) > 5, "Provide valid proof"
        self.proof_of_work = proof
        self.status = STATUS_SUBMITTED


    @gl.public.write
    def evaluate(self):
        assert self.status == STATUS_SUBMITTED, "Work not submitted"

        prompt = f"""
        You are a strict and fair evaluator.

        Job:
        {self.job_description}

        Criteria:
        {self.acceptance_criteria}

        Work:
        {self.proof_of_work}

        Rules:
        - Answer ONLY YES or NO
        - YES = work meets criteria
        - NO = work does not meet criteria
        """

        # 🔥 Equivalence Principle + Consensus
        def ai_call():
            return gl.exec_prompt(prompt)

        result = gl.eq_principle_strict_eq(ai_call)

        approved = "YES" in result.upper()

        # Save reasoning (important for transparency)
        self.ai_reasoning = result

        if approved:
            self.status = STATUS_COMPLETED
            gl.transfer(self.freelancer, self.payment_amount)
            self.ai_verdict = "APPROVED"
        else:
            self.status = STATUS_DISPUTED
            gl.transfer(self.client, self.payment_amount)
            self.ai_verdict = "REJECTED"


    @gl.public.view
    def get_status(self) -> str:
        return self.status


    @gl.public.view
    def get_verdict(self) -> str:
        return self.ai_verdict


    @gl.public.view
    def get_full_result(self) -> str:
        return f"{self.ai_verdict} | {self.ai_reasoning}"
