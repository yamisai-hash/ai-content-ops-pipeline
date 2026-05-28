# generate_one_reel.py -- ideate + (mock) render one reel, then queue it for MANUAL approval.
# Nothing is posted. Posting is gated behind the safety layer.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ideation_agent import propose_idea
from render_pipeline import render_reel
from posting_safety import PostingSafety

def main():
    idea = propose_idea(brand="UNTAINED", product="TEE")
    asset = render_reel(idea)                            # FFmpeg/TTS (mocked in showcase)
    gate = PostingSafety(safe_mode=True)
    result = gate.queue_for_approval(asset)
    print(result)                                        # -> queued, awaiting human approval

if __name__ == "__main__":
    main()
