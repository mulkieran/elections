from collections import Counter
from operator import indexOf


def candidates_for_election(election):
    """
    :param election: voting results
    :type election: list of list of int
    :returns: all candidates in election
    :rtype: list of int
    """
    return frozenset((n for vote in election for n in vote))


def plurality(election):
    """
    :param election: voting results
    :type election: list of list of int
    :returns: the winner of the election by plurality voting algorithm
    :rtype: int or NoneType if there was a tie
    """
    counts = Counter(vote[0] for vote in election)
    winning_score = max(counts.values())
    winners = [c for c, v in counts.items() if v == winning_score]
    if len(winners) > 1:
        return None
    else:
        return winners[0]


def irv(election):
    """
    :param election: voting results
    :type election: list of list of int
    :returns: the winner of the election by instant runoff voting algorithm
    :rtype: int or NoneType if there was a tie
    """
    candidates = candidates_for_election(election)
    while len(candidates) > 1:
        scores = Counter(next(v for v in vote if v in candidates) for vote in election)
        losing_score = min(scores[c] for c in candidates)
        candidates = [c for c in candidates if scores[c] > losing_score]

    if not candidates:
        return None
    else:
        return candidates[0]


def rcv(election):
    """
    :param election: voting results
    :type election: list of list of int
    :returns: the winner of the election by ranked choice voting algorithm
    :rtype: int or NoneType if there was a tie
    """
    candidates = candidates_for_election(election)

    num_voters = len(election)
    fifty_percent_votes = (num_voters // 2) + (0 if num_voters % 2 == 0 else 1)

    while len(candidates) > 1:
        scores = Counter(next(v for v in vote if v in candidates) for vote in election)
        (most_common, count) = scores.most_common(1)[0]
        if count >= fifty_percent_votes:
            return most_common

        losing_score = min(scores[c] for c in candidates)
        candidates = [c for c in candidates if scores[c] > losing_score]

    if not candidates:
        return None
    else:
        return candidates[0]


def majority_preferences(election, choice1, choice2):
    """
    Return the preferences of voters between two candidates in an election.
    """
    return Counter(
        (choice1 if indexOf(vote, choice1) < indexOf(vote, choice2) else choice2)
        for vote in election
    )


import hypothesis.strategies as st


@st.composite
def election(draw):
    """
    Hypthesis strategy that returns an arbitrarily chosen election.

    First chooses an arbitrary number of candidates between 2 and 10 inclusive.
    Then chooses an arbitrary number of voters greater than 1. Then for each
    voter chooses an arbitrary ranking of the candidates. Returns a list of
    lists of the candidates ranked in order by each voter.

    :rtype: list of list of int
    """
    candidates = list(range(draw(st.integers(2, 10))))
    return draw(st.lists(st.permutations(candidates), min_size=1))


from hypothesis import example


def plurality_v_rcv():
    """
    Return an election example where plurality voting yields a different
    winner than RCV voting.

    Assume that in plurality voting, a voter always casts their one vote for
    their first choice, i.e., there are no "strategic" voting choices such
    that the voter votes for a candidate who might win, rather than their
    actual preferred candidate.

    :returns: a tuple of the election, the plurality winner, and the rcv winner
    :rtype: election * int * int
    """
    return (
        election()
        .map(lambda election: (election, plurality(election), rcv(election)))
        .filter(
            lambda res: res[1] is not None and res[2] is not None and res[1] != res[2]
        )
        .example()
    )


def main():
    """
    Select a set of votes such that the winner by the plurality system is
    different from the winner by the ranked choice voting system.
    """
    (votes, plurality_winner, rcv_winner) = plurality_v_rcv()

    print("Plurality winner: %s" % plurality_winner)
    print("RCV winner: %s" % rcv_winner)
    print()
    print("Votes (%s):" % len(votes))
    for vote in votes:
        print(vote)
    print()

    preferred = majority_preferences(votes, plurality_winner, rcv_winner)

    print("Relative preference:")
    for (candidate, count) in preferred.items():
        print("%s voters preferred %s" % (count, candidate))


if __name__ == "__main__":
    main()
