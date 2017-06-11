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
  __RewireAPI__ as detailsRewire,
} from "../../src/modules/details";
import * as Immutable from "immutable";
import {createMockStore, DependenciesStubber} from "../testUtils";
import {__RewireAPI__ as parseDynamicNameRewire} from "./../../src/util/parseDynamicName";
import {ADD_ENTITY_INFO} from "../../src/modules/entities";

describe('(details) detailsReducer', () => {

  it('Should initialize with initial state.', () => {
    expect(detailsReducer(undefined, {})).to.equal(Immutable.fromJS({
      type: null,
    }));
  });

  it('Should return the previous state if an action was not matched.', () => {
    const previousState = Immutable.fromJS({
      type: null,
    });
    let state = detailsReducer(previousState, {});
    expect(state).to.equal(previousState);
  });

  it('Should update the state when character details are supplied.', () => {
    const previousState = Immutable.fromJS({
      type: null,
    });
    let state = detailsReducer(previousState, applyCharacterDetails(0, "DEF"));
    expect(state).to.equal(Immutable.fromJS({
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
    expect(state).to.equal(Immutable.fromJS({
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
    expect(state).to.equal(Immutable.fromJS({
      type: null,
    }));
  });

  it('Should completely remove old state when replaced by a new state.', () => {
    const previousState = Immutable.fromJS({
      type: PANEL_CHARACTER,
      targetId: "DEF",
    });
    let state = detailsReducer(previousState, applyCombatDetails(0, "DEF"));
    expect(state).to.equal(Immutable.fromJS({
      type: PANEL_COMBAT,
      targetId: "DEF",
    }));
  });

  it('Should update the speech of a specified character.', () => {
    let state = decoratedDetailsReducer(undefined, {});
    state = decoratedDetailsReducer(state, applyCombatDetails("HEHE", "DEF"));
    const globalState = Immutable.Map({details: state});

    expect(getDetailsType(fromDetailsState(globalState, "HEHE"))).to.equal(PANEL_COMBAT);
    expect(getDetailsTarget(fromDetailsState(globalState, "HEHE"))).to.equal("DEF");
    expect(getDetailsTarget(fromDetailsState(globalState, "MISSING_CHAR"))).to.equal(null);
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

      const dependencies = new DependenciesStubber(parseDynamicNameRewire, {
        extractActionsFromHtml: (characterId, html) => [],
      });
      dependencies.rewireAll();
      store.dispatch(requestCharacterDetails(charId, targetId));
      store.socketCalledWith("character.get_character_details", charId, targetId);
      const actions = store.getActions();
      expect(actions).to.have.length(2);
      expect(actions[0]).to.deep.equal({
        type: ADD_ENTITY_INFO,
        entityInfo: targetEntityInfo,
        characterId: charId,
      });
      expect(actions[1]).to.deep.equal({
        type: APPLY_DETAILS_CHANGE,
        detailsType: PANEL_CHARACTER,
        characterId: charId,
        targetId: targetId,
      });
      dependencies.unwireAll();
    });

    it('Should request combat details so it can be displayed on a panel.', () => {
      const combatId = "combat1";
      const combatInfo = {
        id: combatId,
        attackers: ["A", "LE"],
        defenders: ["G", "UN"],
      };
      const store = createMockStore({}, [combatInfo]);

      const dependencies = new DependenciesStubber(parseDynamicNameRewire, {
        extractActionsFromHtml: (characterId, html) => [],
      });
      dependencies.rewireAll();

      store.dispatch(requestCombatDetails(charId, combatId));
      store.socketCalledWith("character.get_combat_details", charId, combatId);
      const actions = store.getActions();
      expect(actions).to.have.length(2);
      expect(actions[0]).to.deep.equal({
        type: ADD_ENTITY_INFO,
        entityInfo: combatInfo,
        characterId: charId,
      });
      expect(actions[1]).to.deep.equal({
        type: APPLY_DETAILS_CHANGE,
        detailsType: PANEL_COMBAT,
        characterId: charId,
        targetId: combatId,
      });
      dependencies.unwireAll();
    });

    it('Should edit character name.', () => {
      const targetId = "other_char";
      const newName = "newName";
      const store = createMockStore({}, []);

      let wasRequestCalled = false;
      const dependencies = new DependenciesStubber(detailsRewire, {
        fromDetailsState: () => 1,
        getDetailsTarget: () => targetId,
        requestCharacterDetails: (dispatch) => {
          wasRequestCalled = true;
          return () => {};
        },
      });
      dependencies.rewireAll();
      store.dispatch(submitEditedName(charId, newName));
      store.socketCalledWith("character.rename_entity", charId, targetId, newName);
      const actions = store.getActions();
      expect(actions).to.have.length(0);
      expect(wasRequestCalled).to.be.equal(true);
      dependencies.unwireAll();
    });
  });
});
