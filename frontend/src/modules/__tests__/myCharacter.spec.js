import {
  myCharacterReducer,
  updateMyCharacterState,
  getMyCharacterEntityId,
  fromMyCharacterState, requestMyCharacterInfo, UPDATE_MY_CHARACTER_ID,
} from "../myCharacter";
import * as Immutable from "immutable";
import {createMockStore} from "../../../tests/testUtils";
import {ADD_ENTITY_INFO} from "../entities";

describe('(character) myCharacterReducer', () => {

  it('Should initialize with initial state of empty list.', () => {
    expect(myCharacterReducer(undefined, {})).toEqual(Immutable.fromJS({
      "myCharacterEntityId": null,
    }));
  });

  it('Should return the previous state if an action was not matched.', () => {
    const previousState = Immutable.fromJS({
      "myCharacterEntityId": null,
    });
    let state = myCharacterReducer(previousState, {});
    expect(state).toEqual(previousState);
  });

  it('Should update myCharacter state.', () => {
    let state = myCharacterReducer(undefined, {});
    expect(getMyCharacterEntityId(state)).toEqual(null);

    state = myCharacterReducer(state, updateMyCharacterState("ALA", "eaf18"));
    expect(getMyCharacterEntityId(state)).toEqual("eaf18");
  });

  it('Should request detailed info about my character.', () => {
    const charId = "DELELE";
    const charEntityId = "jwi13";
    const characterInfo = {
      id: charEntityId,
      name: "Jonathan",
    };

    const store = createMockStore({}, [characterInfo]);

    store.dispatch(requestMyCharacterInfo(charId));
    store.socketCalledWith("character.get_my_character_info", charId);

    const actions = store.getActions();
    expect(actions).toHaveLength(2);
    expect(actions[0]).toEqual({
      type: UPDATE_MY_CHARACTER_ID,
      characterId: charId,
      myCharacterEntityId: charEntityId,
    });
    expect(actions[1]).toEqual({
      type: ADD_ENTITY_INFO,
      entityInfo: characterInfo,
      characterId: charId,
    });
  });
});
