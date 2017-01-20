import {
  playerReducer,
  updateOwnCharactersList, updateAchievementsList,
} from "../../src/modules/player";
import * as Immutable from "immutable";

describe('(player) playerReducer', () => {

  it('Should initialize with initial state of empty list.', () => {
    expect(playerReducer(undefined, {})).to.equal(Immutable.fromJS({
      ownCharacters: [],
      achievements: [],
    }));
  });

  it('Should return the previous state if an action was not matched.', () => {
    const previousState = Immutable.fromJS({
      ownCharacters: [],
      achievements: [],
    });
    let state = playerReducer(previousState, {});
    expect(state).to.equal(previousState);
  });

  describe('ownCharacters', () => {

    it('Should update the state if empty list is supplied.', () => {
      const previousState = Immutable.fromJS({
        ownCharacters: [
          {id: 1, name: "john"}, {id: 7, name: "ally"}
        ],
        achievements: [],
      });
      let state = playerReducer(previousState, updateOwnCharactersList([]));
      expect(state).to.equal(previousState.setIn(["ownCharacters"], Immutable.List()));
    });

    it('Should update the state if new list is supplied.', () => {
      const previousState = Immutable.fromJS({
        ownCharacters: [
          {id: 1, name: "john"}, {id: 7, name: "ally"}
        ],
        achievements: [],
      });
      let state = playerReducer(previousState, updateOwnCharactersList([{id: 11, name: "ad"}]));
      expect(state).to.equal(previousState.setIn(["ownCharacters"],
        Immutable.fromJS([{id: 11, name: "ad"}])));
    });
  });

  describe('achievements', () => {

    it('Should return the previous state if an action was not matched.', () => {
      const previousState = Immutable.Map({achievements: []});
      let state = playerReducer(previousState, {});
      expect(state).to.equal(previousState);
    });

    it('Should update the state.', () => {
      const previousState = Immutable.Map({achievements: Immutable.List()});
      let state = playerReducer(previousState,
        updateAchievementsList(
          [{title: "abc", content: "be able to read abc"}]
        ));
      expect(state).to.equal(Immutable.fromJS({
        achievements: [{title: "abc", content: "be able to read abc"}]
      }));
    });
  });
});


