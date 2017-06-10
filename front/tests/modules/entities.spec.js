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
  decoratedEntitiesReducer,
  updateItemsInInventoryList,
  requestRefreshEntity,
  __RewireAPI__ as entitiesRewire, ADD_ENTITY_INFO, UPDATE_CHILDREN_OF_ENTITY, REMOVE_CHILD_OF_ENTITY,
  requestRootEntities, UPDATE_ROOT_ENTITIES_LIST, requestInventoryEntities, UPDATE_ITEMS_IN_INVENTORY_LIST
} from "../../src/modules/entities";
import * as Immutable from "immutable";
import {createMockStore, DependenciesStubber} from "../testUtils";

describe('(entities) entitiesReducer', () => {
  it('Should initialize with initial state of empty list.', () => {
    expect(entitiesReducer(undefined, {})).to.equal(Immutable.fromJS({
      rootEntities: [],
      itemsInInventory: [],
      children: {},
      info: {},
      expanded: Immutable.Set(),
      selected: Immutable.Set(),
      actionType: null,
      actionDetails: Immutable.Map(),
      selectedDetails: null,
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
      actionType: null,
      actionDetails: Immutable.Map(),
      selectedDetails: null,
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
      actionType: null,
      actionDetails: Immutable.Map(),
      selectedDetails: null,
    });
    let state = entitiesReducer(previousState, updateRootEntitiesList(0, ["ABC", "DEF"]));
    expect(state).to.equal(Immutable.fromJS({
      rootEntities: ["ABC", "DEF"],
      itemsInInventory: [],
      children: {},
      info: {},
      expanded: Immutable.Set(),
      selected: Immutable.Set(),
      actionType: null,
      actionDetails: Immutable.Map(),
      selectedDetails: null,
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
      actionType: null,
      actionDetails: Immutable.Map(),
      selectedDetails: null,
    });
    let state = entitiesReducer(previousState, updateItemsInInventoryList(0, ["HEJ", "TAM"]));
    expect(state).to.equal(Immutable.fromJS({
      rootEntities: [],
      itemsInInventory: ["HEJ", "TAM"],
      children: {},
      info: {},
      expanded: Immutable.Set(),
      selected: Immutable.Set(),
      actionType: null,
      actionDetails: Immutable.Map(),
      selectedDetails: null,
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
      actionType: null,
      actionDetails: Immutable.Map(),
      selectedDetails: null,
    });

    let state = entitiesReducer(previousState, removeChildOfEntity(0, "BAF", "CBA"));
    expect(state).to.equal(Immutable.fromJS({
      rootEntities: [],
      itemsInInventory: [],
      children: {"BAF": ["DOM"]},
      info: {},
      expanded: Immutable.Set(),
      selected: Immutable.Set(),
      actionType: null,
      actionDetails: Immutable.Map(),
      selectedDetails: null,
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
      actionType: null,
      actionDetails: Immutable.Map(),
      selectedDetails: null,
    });
    let state = entitiesReducer(previousState, updateChildrenOfEntity(0, "BAF", ["CBA", "DOM"]));
    expect(state).to.equal(Immutable.fromJS({
      rootEntities: [],
      itemsInInventory: [],
      children: {"BAF": ["CBA", "DOM"]},
      info: {},
      expanded: Immutable.Set(),
      selected: Immutable.Set(),
      actionType: null,
      actionDetails: Immutable.Map(),
      selectedDetails: null,
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
      actionType: null,
      actionDetails: Immutable.Map(),
      selectedDetails: null,
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
      actionType: null,
      actionDetails: Immutable.Map(),
      selectedDetails: null,
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
          actionType: null,
          actionDetails: Immutable.Map(),
          selectedDetails: null,
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

  describe("Asynchronous socketio actions to refresh an entity", () => {
    const charId = "DEF";

    it('Should request refresh of entity that is not visible.', () => {
      const itemId = "HAMMER_1";

      const dependencies = new DependenciesStubber(entitiesRewire, {
        fromEntitiesState: () => 1,
        getChildren: () => Immutable.Map(),
        getEntityInfos: () => Immutable.fromJS({
          [itemId]: {
            id: itemId,
            name: "hammer",
          }
        }),
        getItemsInInventory: () => Immutable.List(),
      });
      dependencies.rewireAll();

      const store = createMockStore({}, null);

      store.dispatch(requestRefreshEntity(charId, itemId));
      store.socketNotCalled();

      const actions = store.getActions();
      expect(actions).to.have.length(0);
      dependencies.unwireAll();
    });

    it('Should request refresh of entity that is inventory.', () => {
      const itemId = "HAMMER_1";
      const newItemInfo = {
        id: itemId,
        name: "new hammer",
        activities: [],
      };

      const dependencies = new DependenciesStubber(entitiesRewire, {
        fromEntitiesState: () => 1,
        getChildren: () => Immutable.Map(),
        getEntityInfos: () => Immutable.fromJS({
          [itemId]: {
            id: itemId,
            name: "old hammer",
          }
        }),
        getItemsInInventory: () => Immutable.List([itemId]),
      });
      dependencies.rewireAll();

      const store = createMockStore({}, [{
        id: itemId,
        children: [],
        info: newItemInfo,
      }]);

      store.dispatch(requestRefreshEntity(charId, itemId));
      store.socketCalledWith("character.get_extended_entity_info", charId, itemId, null);

      const actions = store.getActions();
      expect(actions).to.have.length(2);
      expect(actions[0]).to.deep.equal({
        type: ADD_ENTITY_INFO,
        entityInfo: newItemInfo,
        characterId: charId,
      });
      expect(actions[1]).to.deep.equal({
        type: UPDATE_CHILDREN_OF_ENTITY,
        parentEntityId: itemId,
        childrenIds: [],
        characterId: charId,
      });

      dependencies.unwireAll();
    });

    it('Should request refresh of entity with 2 activities that is on the ground.', () => {
      const itemId = "HAMMER_1";
      const parentIdOfItem = "PARENT_OF_HAMMER_1";
      const activity1 = {
        id: "activity1",
        name: "forging a sword",
        requirements: "many",
      };
      const activity2 = {
        id: "activity2",
        name: "smithing a hammer",
        requirements: "a few",
      };
      const newItemInfo = {
        id: itemId,
        name: "new hammer",
        activities: [
          activity1,
          activity2,
        ],
      };

      const dependencies = new DependenciesStubber(entitiesRewire, {
        fromEntitiesState: () => 1,
        getChildren: () => Immutable.fromJS({
          [parentIdOfItem]: [itemId],
        }),
        getEntityInfos: () => Immutable.fromJS({
          [itemId]: {
            id: itemId,
            name: "old hammer",
          }
        }),
        getItemsInInventory: () => Immutable.List(),
      });
      dependencies.rewireAll();

      const store = createMockStore({}, [{
        id: itemId,
        children: [],
        info: newItemInfo,
      }]);

      store.dispatch(requestRefreshEntity(charId, itemId));
      store.socketCalledWith("character.get_extended_entity_info", charId, itemId, parentIdOfItem);

      const actions = store.getActions();
      expect(actions).to.have.length(4);
      expect(actions[0]).to.deep.equal({
        type: ADD_ENTITY_INFO,
        entityInfo: activity1,
        characterId: charId,
      });
      expect(actions[1]).to.deep.equal({
        type: ADD_ENTITY_INFO,
        entityInfo: activity2,
        characterId: charId,
      });
      expect(actions[2]).to.deep.equal({
        type: ADD_ENTITY_INFO,
        entityInfo: newItemInfo,
        characterId: charId,
      });
      expect(actions[3]).to.deep.equal({
        type: UPDATE_CHILDREN_OF_ENTITY,
        parentEntityId: itemId,
        childrenIds: [],
        characterId: charId,
      });

      dependencies.unwireAll();
    });

    it('Should request refresh of entity that was visible on the ground but disappears.', () => {
      const itemId = "HAMMER_1";
      const parentIdOfItem = "PARENT_OF_HAMMER_1";

      const dependencies = new DependenciesStubber(entitiesRewire, {
        fromEntitiesState: () => 1,
        getChildren: () => Immutable.fromJS({
          [parentIdOfItem]: [itemId],
        }),
        getEntityInfos: () => Immutable.fromJS({
          [itemId]: {
            id: itemId,
            name: "hammer",
          }
        }),
        getItemsInInventory: () => Immutable.List(),
      });
      dependencies.rewireAll();

      const store = createMockStore({}, [{
        id: itemId,
        children: [],
        info: null,
      }]);

      store.dispatch(requestRefreshEntity(charId, itemId));
      store.socketCalledWith("character.get_extended_entity_info", charId, itemId, parentIdOfItem);

      const actions = store.getActions();
      expect(actions).to.have.length(1);
      expect(actions[0]).to.deep.equal({
        type: REMOVE_CHILD_OF_ENTITY,
        parentEntityId: parentIdOfItem,
        childId: itemId,
        characterId: charId,
      });

      dependencies.unwireAll();
    });

    it('Should request refresh of entity which is visible', () => {
      const activityId = "activity_on_HAMMER_1";
      const itemId = "HAMMER_1";
      const parentIdOfItem = "PARENT_OF_HAMMER_1";
      const newActivityInfo = {
        id: activityId,
        name: "quickly repairing a hammer",
        parent: itemId,
      };
      const newItemInfo = {
        id: itemId,
        name: "new hammer",
        activities: [
          newActivityInfo,
        ],
      };

      const dependencies = new DependenciesStubber(entitiesRewire, {
        fromEntitiesState: () => 1,
        getChildren: () => Immutable.fromJS({
          [parentIdOfItem]: [itemId],
        }),
        getEntityInfos: () => Immutable.fromJS({
          [itemId]: {
            id: itemId,
            name: "hammer",
            activities: [activityId],
          },
          [activityId]: {
            id: activityId,
            name: "repairing hammer",
            parent: itemId,
          },
        }),
        getItemsInInventory: () => Immutable.List(),
      });
      dependencies.rewireAll();

      const store = createMockStore({}, [{
        id: itemId,
        children: [],
        info: newItemInfo,
      }]);

      store.dispatch(requestRefreshEntity(charId, activityId));
      store.socketCalledWith("character.get_extended_entity_info", charId, itemId, parentIdOfItem);

      const actions = store.getActions();
      expect(actions).to.have.length(3);
      expect(actions[0]).to.deep.equal({
        type: ADD_ENTITY_INFO,
        entityInfo: newActivityInfo,
        characterId: charId,
      });
      expect(actions[1]).to.deep.equal({
        type: ADD_ENTITY_INFO,
        entityInfo: {
          id: itemId,
          name: "new hammer",
          activities: [activityId],
        },
        characterId: charId,
      });
      expect(actions[2]).to.deep.equal({
        type: UPDATE_CHILDREN_OF_ENTITY,
        parentEntityId: itemId,
        childrenIds: [],
        characterId: charId,
      });
      dependencies.unwireAll();
    });
  });

  it('Should request root entities.', () => {
    const charId = "DEF";
    const item1Id = "HAMMER_1";
    const item1 = {
      id: item1Id,
      name: "hammer",
      activities: [],
    };
    const item2Id = "SWORD_2";
    const activityIdOfItem2 = "activity_on_SWORD_2";
    const activityOfItem2 = {
      id: activityIdOfItem2,
      name: "polishing a sword",
      parent: item2Id,
    };
    const item2 = {
      id: item2Id,
      name: "sword",
      activities: [activityOfItem2],
    };

    const store = createMockStore({}, [
      [
        item1,
        item2,
      ],
    ]);

    store.dispatch(requestRootEntities(charId));
    store.socketCalledWith("character.get_root_entities", charId);

    const actions = store.getActions();
    expect(actions).to.have.length(4);
    expect(actions[0]).to.deep.equal({
      type: ADD_ENTITY_INFO,
      entityInfo: item1,
      characterId: charId,
    });
    expect(actions[1]).to.deep.equal({
      type: ADD_ENTITY_INFO,
      entityInfo: activityOfItem2,
      characterId: charId,
    });
    expect(actions[2]).to.deep.equal({
      type: ADD_ENTITY_INFO,
      entityInfo: {
        id: item2Id,
        name: "sword",
        activities: [activityIdOfItem2],
      },
      characterId: charId,
    });
    expect(actions[3]).to.deep.equal({
      type: UPDATE_ROOT_ENTITIES_LIST,
      rootEntitiesList: [item1Id, item2Id],
      characterId: charId,
    });
  });

  it('Should request entities in inventory.', () => {
    const charId = "DEF";
    const item1Id = "HAMMER_1";
    const item1 = {
      id: item1Id,
      name: "hammer",
      activities: [],
    };
    const item2Id = "SWORD_2";
    const activityIdOfItem2 = "activity_on_SWORD_2";
    const activityOfItem2 = {
      id: activityIdOfItem2,
      name: "polishing a sword",
      parent: item2Id,
    };
    const item2 = {
      id: item2Id,
      name: "sword",
      activities: [activityOfItem2],
    };

    const store = createMockStore({}, [
      [
        item1,
        item2,
      ],
    ]);

    store.dispatch(requestInventoryEntities(charId));
    store.socketCalledWith("character.get_items_in_inventory", charId);

    const actions = store.getActions();
    expect(actions).to.have.length(4);
    expect(actions[0]).to.deep.equal({
      type: ADD_ENTITY_INFO,
      entityInfo: item1,
      characterId: charId,
    });
    expect(actions[1]).to.deep.equal({
      type: ADD_ENTITY_INFO,
      entityInfo: activityOfItem2,
      characterId: charId,
    });
    expect(actions[2]).to.deep.equal({
      type: ADD_ENTITY_INFO,
      entityInfo: {
        id: item2Id,
        name: "sword",
        activities: [activityIdOfItem2],
      },
      characterId: charId,
    });
    expect(actions[3]).to.deep.equal({
      type: UPDATE_ITEMS_IN_INVENTORY_LIST,
      itemsList: [item1Id, item2Id],
      characterId: charId,
    });
  });
});


