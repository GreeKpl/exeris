import {
  myCharacterReducer,
  updateMyCharacterState,
  getMyCharacterEntityId,
  fromMyCharacterState, requestMyCharacterInfo, UPDATE_MY_CHARACTER_ID,
} from "../../src/modules/myCharacter";
import * as Immutable from "immutable";
import {createMockStore} from "../testUtils";
import {ADD_ENTITY_INFO} from "../../src/modules/entities";

describe('(character) myCharacterReducer', () => {

  it('Should initialize with initial state of empty list.', () => {
    expect(myCharacterReducer(undefined, {})).to.equal(Immutable.fromJS({
      "myCharacterEntityId": null,
    }));
  });

  it('Should return the previous state if an action was not matched.', () => {
    const previousState = Immutable.fromJS({
      "myCharacterEntityId": null,
    });
    let state = myCharacterReducer(previousState, {});
    expect(state).to.equal(previousState);
  });

  it('Should update myCharacter state.', () => {
    let state = myCharacterReducer(undefined, {});
    expect(getMyCharacterEntityId(state)).to.equal(null);

    state = myCharacterReducer(state, updateMyCharacterState("ALA", "eaf18"));
    expect(getMyCharacterEntityId(state)).to.equal("eaf18");
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
    expect(actions).to.have.length(2);
    expect(actions[0]).to.deep.equal({
      type: UPDATE_MY_CHARACTER_ID,
      characterId: charId,
      myCharacterEntityId: charEntityId,
    });
    expect(actions[1]).to.deep.equal({
      type: ADD_ENTITY_INFO,
      entityInfo: characterInfo,
      characterId: charId,
    });
  });
});
