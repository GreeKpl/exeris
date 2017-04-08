import {
  myCharacterReducer,
  updateMyCharacterState,
  getMyCharacterEntityId,
  fromMyCharacterState,
} from "../../src/modules/myCharacter";
import * as Immutable from "immutable";

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
});
