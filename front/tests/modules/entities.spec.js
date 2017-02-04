import {
  addEntityInfo,
  updateRootEntitiesList,
  updateChildrenOfEntity,
  removeChildOfEntity,
  getChildren,
  getRootEntities,
  getEntityInfos,
  fromEntitiesState,
  entitiesReducer,
  decoratedEntitiesReducer, updateItemsInInventoryList
} from "../../src/modules/entities";
import * as Immutable from "immutable";

describe('(entities) entitiesReducer', () => {

  it('Should initialize with initial state of empty list.', () => {
    expect(entitiesReducer(undefined, {})).to.equal(Immutable.fromJS({
      rootEntities: [],
      itemsInInventory: [],
      children: {},
      info: {},
      expanded: Immutable.Set(),
      selected: Immutable.Set(),
    }));
  });

  it('Should return the previous state if an action was not matched.', () => {
    const previousState = Immutable.fromJS({
      rootEntities: [],
      itemsInInventory: [],
      children: {"DEF": ["ABA"]},
      info: {},
      expanded: Immutable.Set(),
      selected: Immutable.Set(),
    });
    let state = entitiesReducer(previousState, {});
    expect(state).to.equal(previousState);
  });

  it('Should update the rootEntities.', () => {
    const previousState = Immutable.fromJS({
      rootEntities: [],
      itemsInInventory: [],
      children: {},
      info: {},
      expanded: Immutable.Set(),
      selected: Immutable.Set(),
    });
    let state = entitiesReducer(previousState, updateRootEntitiesList(0, ["ABC", "DEF"]));
    expect(state).to.equal(Immutable.fromJS({
      rootEntities: ["ABC", "DEF"],
      itemsInInventory: [],
      children: {},
      info: {},
      expanded: Immutable.Set(),
      selected: Immutable.Set(),
    }));
  });


  it('Should update the itemsInInventory.', () => {
    const previousState = Immutable.fromJS({
      rootEntities: [],
      itemsInInventory: [],
      children: {},
      info: {},
      expanded: Immutable.Set(),
      selected: Immutable.Set(),
    });
    let state = entitiesReducer(previousState, updateItemsInInventoryList(0, ["HEJ", "TAM"]));
    expect(state).to.equal(Immutable.fromJS({
      rootEntities: [],
      itemsInInventory: ["HEJ", "TAM"],
      children: {},
      info: {},
      expanded: Immutable.Set(),
      selected: Immutable.Set(),
    }));
  });

  it('Should remove the child.', () => {
    const previousState = Immutable.fromJS({
      rootEntities: [],
      itemsInInventory: [],
      children: {"BAF": ["CBA", "DOM"]},
      info: {},
      expanded: Immutable.Set(),
      selected: Immutable.Set(),
    });

    let state = entitiesReducer(previousState, removeChildOfEntity(0, "BAF", "CBA"));
    expect(state).to.equal(Immutable.fromJS({
      rootEntities: [],
      itemsInInventory: [],
      children: {"BAF": ["DOM"]},
      info: {},
      expanded: Immutable.Set(),
      selected: Immutable.Set(),
    }));
  });

  it('Should update the children.', () => {
    const previousState = Immutable.fromJS({
      rootEntities: [],
      itemsInInventory: [],
      children: {},
      info: {},
      expanded: Immutable.Set(),
      selected: Immutable.Set(),
    });
    let state = entitiesReducer(previousState, updateChildrenOfEntity(0, "BAF", ["CBA", "DOM"]));
    expect(state).to.equal(Immutable.fromJS({
      rootEntities: [],
      itemsInInventory: [],
      children: {"BAF": ["CBA", "DOM"]},
      info: {},
      expanded: Immutable.Set(),
      selected: Immutable.Set(),
    }));
  });

  it('Should update the info.', () => {
    let state = Immutable.fromJS({
      rootEntities: [],
      itemsInInventory: [],
      children: {},
      info: {},
      expanded: Immutable.Set(),
      selected: Immutable.Set(),
    });
    state = entitiesReducer(state, addEntityInfo(0, {
      id: "BAC",
      name: "a house",
    }));
    state = entitiesReducer(state, addEntityInfo(0, {
      id: "CAN",
      name: "a hammer",
    }));
    expect(state).to.equal(Immutable.fromJS({
      rootEntities: [],
      itemsInInventory: [],
      children: {},
      info: {"BAC": {id: "BAC", name: "a house"}, "CAN": {id: "CAN", name: "a hammer"}},
      expanded: Immutable.Set(),
      selected: Immutable.Set(),
    }));
  });

  it('Should work for decorated reducer.', () => {
    let state = decoratedEntitiesReducer(undefined, {});
    state = decoratedEntitiesReducer(state, addEntityInfo("CHAR", {
      id: "CAN",
      name: "a chest",
    }));
    state = decoratedEntitiesReducer(state, addEntityInfo("CHAR", {
      id: "KLA",
      name: "a hammer",
    }));
    state = decoratedEntitiesReducer(state, updateRootEntitiesList("CHAR", ["CAN"]));
    state = decoratedEntitiesReducer(state, updateChildrenOfEntity("CHAR", "CAN", ["KLA"]));

    const globalState = Immutable.Map({entities: state});

    expect(globalState).to.equal(Immutable.fromJS({
      entities: {
        "CHAR": {
          rootEntities: ["CAN"],
          itemsInInventory: [],
          children: {"CAN": ["KLA"]},
          info: {
            "CAN": {
              id: "CAN",
              name: "a chest",
            },
            "KLA": {
              id: "KLA",
              name: "a hammer",
            }
          },
          expanded: Immutable.Set(),
          selected: Immutable.Set(),
        }
      },
    }));

    expect(getChildren(fromEntitiesState(globalState, "CHAR")))
      .to.equal(Immutable.fromJS({
      "CAN": ["KLA"],
    }));

    expect(getRootEntities(fromEntitiesState(globalState, "CHAR")))
      .to.equal(Immutable.List.of("CAN"));
    expect(getEntityInfos(fromEntitiesState(globalState, "CHAR")))
      .to.equal(Immutable.fromJS({
      "KLA": {
        id: "KLA",
        name: "a hammer",
      },
      "CAN": {
        id: "CAN",
        name: "a chest",
      },
    }));
  });
});


