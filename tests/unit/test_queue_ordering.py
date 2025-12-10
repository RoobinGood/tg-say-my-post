from src.utils.queue import InMemoryQueue


def test_queue_order_per_chat():
    q = InMemoryQueue()
    j1 = q.enqueue(1, "a", "p1")
    j2 = q.enqueue(1, "b", "p2")
    j3 = q.enqueue(2, "c", "p3")
    assert j1.order == 1
    assert j2.order == 2
    assert j3.order == 1  # separate chat
    assert q.next_job(1).job_id == "a"
    q.pop_job(1)
    assert q.next_job(1).job_id == "b"
    assert q.next_job(2).job_id == "c"


