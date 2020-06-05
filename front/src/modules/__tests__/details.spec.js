import {
  PANEL_COMBAT,
  PANEL_CHARACTER,
  APPLY_DETAILS_CHANGE,
  applyCharacterDetails,
  applyCombatDetails,
  closeDetails,
  getDetailsType,
  fromDetailsState,
  detailsReducer,
  decoratedDetailsReducer,
  getDetailsTarget,
  requestCharacterDetails,
  requestCombatDetails,
  submitEditedName,
} from "../details";
import * as Immutable from "immutable";
import {createMockStore, DependenciesStubber} from "../../../tests/testUtils";
import {__RewireAPI__ as parseDynamicNameRewire} from "../../util/parseDynamicName";
import {ADD_ENTITY_INFO} from "../entities";

describe('(details) detailsReducer', () => {

  it('Should initialize with initial state.', () => {
    expect(detailsReducer(undefined, {})).toEqual(Immutable.fromJS({
      type: null,
    }));
  });

  it('Should return the previous state if an action was not matched.', () => {
    const previousState = Immutable.fromJS({
      type: null,
    });
    let state = detailsReducer(previousState, {});
    expect(state).toEqual(previousState);
  });

  it('Should update the state when character details are supplied.', () => {
    const previousState = Immutable.fromJS({
      type: null,
    });
    let state = detailsReducer(previousState, applyCharacterDetails(0, "DEF"));
    expect(state).toEqual(Immutable.fromJS({
        type: PANEL_CHARACTER,
        targetId: "DEF",
      }
    ));
  });

  it('Should update the state when combat details are supplied.', () => {
    const previousState = Immutable.fromJS({
      type: null,
    });
    let state = detailsReducer(previousState, applyCombatDetails(0, "DEF"));
    expect(state).toEqual(Immutable.fromJS({
      type: PANEL_COMBAT,
      targetId: "DEF",
    }));
  });

  it('Should clear the state on close action.', () => {
    const previousState = Immutable.fromJS({
      type: PANEL_CHARACTER,
      id: "DEF",
      name: "John",
      locationName: "Place",
      locationId: "123",
      workIntent: "",
    });
    let state = detailsReducer(previousState, closeDetails(0));
    expect(state).toEqual(Immutable.fromJS({
      type: null,
    }));
  });

  it('Should completely remove old state when replaced by a new state.', () => {
    const previousState = Immutable.fromJS({
      type: PANEL_CHARACTER,
      targetId: "DEF",
    });
    let state = detailsReducer(previousState, applyCombatDetails(0, "DEF"));
    expect(state).toEqual(Immutable.fromJS({
      type: PANEL_COMBAT,
      targetId: "DEF",
    }));
  });

  it('Should update the speech of a specified character.', () => {
    let state = decoratedDetailsReducer(undefined, {});
    state = decoratedDetailsReducer(state, applyCombatDetails("HEHE", "DEF"));
    const globalState = Immutable.Map({details: state});

    expect(getDetailsType(fromDetailsState(globalState, "HEHE"))).toEqual(PANEL_COMBAT);
    expect(getDetailsTarget(fromDetailsState(globalState, "HEHE"))).toEqual("DEF");
    expect(getDetailsTarget(fromDetailsState(globalState, "MISSING_CHAR"))).toEqual(null);
  });

  describe("Asynchronous socketio actions", () => {
    const charId = "MYCHAR";

    it('Should request character details to show in a panel.', () => {
      const targetId = "target_char";
      const targetEntityInfo = {
        id: targetId,
        detail1: "hey",
        detail2: "ho",
      };
      const store = createMockStore({}, [targetEntityInfo]);

      store.dispatch(requestCharacterDetails(charId, targetId));
      store.socketCalledWith("character.get_character_details", charId, targetId);
      const actions = store.getActions();
      expect(actions).toHaveLength(2);
      expect(actions[0]).toEqual({
        type: ADD_ENTITY_INFO,
        entityInfo: targetEntityInfo,
        characterId: charId,
      });
      expect(actions[1]).toEqual({
        type: APPLY_DETAILS_CHANGE,
        detailsType: PANEL_CHARACTER,
        characterId: charId,
        targetId: targetId,
      });
    });

    it('Should request combat details so it can be displayed on a panel.', () => {
      const combatId = "combat1";
      const combatInfo = {
        id: combatId,
        attackers: ["A", "LE"],
        defenders: ["G", "UN"],
      };
      const store = createMockStore({}, [combatInfo]);

      store.dispatch(requestCombatDetails(charId, combatId));
      store.socketCalledWith("character.get_combat_details", charId, combatId);
      const actions = store.getActions();
      expect(actions).toHaveLength(2);
      expect(actions[0]).toEqual({
        type: ADD_ENTITY_INFO,
        entityInfo: combatInfo,
        characterId: charId,
      });
      expect(actions[1]).toEqual({
        type: APPLY_DETAILS_CHANGE,
        detailsType: PANEL_COMBAT,
        characterId: charId,
        targetId: combatId,
      });
    });

    it('Should edit character name', () => {
      const targetId = "other_char";
      const newName = "newName";
      const store = createMockStore(Immutable.fromJS({
        details: {
          [charId]: {
            targetId,
          },
        },
      }), [{name: "newName"}]);

      store.dispatch(submitEditedName(charId, newName));
      store.socketCalledWith("character.rename_entity", charId, targetId, newName);
      const actions = store.getActions();
      expect(actions).toHaveLength(2); // TODO changed from 0 when refactoring tests, it's probably better since calls are no longer mocked
    });
  });
});
