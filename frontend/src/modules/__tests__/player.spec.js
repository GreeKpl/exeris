import {
  playerReducer,
  updateOwnCharactersList, updateAchievementsList, requestOwnCharactersList, UPDATE_OWN_CHARACTERS_LIST,
  createNewCharacter, UPDATE_ACHIEVEMENTS_LIST, requestAchievementsList,
} from "../player";
import * as Immutable from "immutable";
import {createMockStore} from "../../../tests/testUtils";

describe('(player) playerReducer', () => {

  it('Should initialize with initial state of empty list.', () => {
    expect(playerReducer(undefined, {})).toEqual(Immutable.fromJS({
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
    expect(state).toEqual(previousState);
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
      expect(state).toEqual(previousState.setIn(["ownCharacters"], Immutable.List()));
    });

    it('Should update the state if new list is supplied.', () => {
      const previousState = Immutable.fromJS({
        ownCharacters: [
          {id: 1, name: "john"}, {id: 7, name: "ally"}
        ],
        achievements: [],
      });
      let state = playerReducer(previousState, updateOwnCharactersList([{id: 11, name: "ad"}]));
      expect(state).toEqual(previousState.setIn(["ownCharacters"],
        Immutable.fromJS([{id: 11, name: "ad"}])));
    });

    const charId = "DEF";

    it('Should request own characters list.', () => {
      const charactersList = [
        {
          id: "ALA",
          name: "John",
        },
        {
          id: "REQ",
          name: "Sally",
        },
      ];

      const store = createMockStore({}, [charactersList]);

      store.dispatch(requestOwnCharactersList());
      store.socketCalledWith("player.get_characters_list");

      const actions = store.getActions();
      expect(actions).toHaveLength(1);
      expect(actions[0]).toEqual({
        type: UPDATE_OWN_CHARACTERS_LIST,
        characterIdsList: charactersList,
      });
    });

    it('Should request creation of a new character.', () => {
      const store = createMockStore({}, []);
      const newCharName = "NEW_CHAR_NAME";
      store.dispatch(createNewCharacter(newCharName));
      store.socketCalledWith("player.create_new_character", newCharName);
      store.socketCalledWith("player.get_characters_list");
    });
  });

  describe('achievements', () => {

    it('Should return the previous state if an action was not matched.', () => {
      const previousState = Immutable.Map({achievements: []});
      let state = playerReducer(previousState, {});
      expect(state).toEqual(previousState);
    });

    it('Should update the state.', () => {
      const previousState = Immutable.Map({achievements: Immutable.List()});
      let state = playerReducer(previousState,
        updateAchievementsList(
          [{title: "abc", content: "be able to read abc"}]
        ));
      expect(state).toEqual(Immutable.fromJS({
        achievements: [{title: "abc", content: "be able to read abc"}]
      }));
    });

    const charId = "DEF";

    it('Should request achievements list.', () => {
      const achievementsList = [
        {
          name: "Potato eater",
        },
        {
          name: "Cookie clicker",
        },
      ];

      const store = createMockStore({}, [achievementsList]);

      store.dispatch(requestAchievementsList());
      store.socketCalledWith("player.get_achievements_list");

      const actions = store.getActions();
      expect(actions).toHaveLength(1);
      expect(actions[0]).toEqual({
        type: UPDATE_ACHIEVEMENTS_LIST,
        achievementsList: achievementsList,
      });
    });
  });
});


