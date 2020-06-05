import * as Immutable from "immutable";
import {mount} from "enzyme";
import * as React from "react";
import {ActionsList} from "../ActionsListContainer";

describe('(component) ActionsList', () => {

  const actionsList = Immutable.fromJS([
    {
      id: "FIRST",
      name: "collecting_potatoes",
      enabled: true,
    },
    {
      id: "SECOND",
      name: "collecting_grapes",
      enabled: false,
    }
  ]);

  it('Should render empty list when no data specified.', () => {
    const requestStateMock = jest.fn();
    const testedComponent = mount(<ActionsList actionsList={Immutable.Map()}
                                               requestState={requestStateMock}/>);

    expect(testedComponent.find("ListGroup").children()).toHaveLength(0);
    expect(requestStateMock).toHaveBeenCalled();
  });

  it('Should render simple list with one enabled and one disabled action.', () => {
    const requestStateMock = jest.fn();

    const testedComponent = mount(<ActionsList actionsList={actionsList}
                                               requestState={requestStateMock}/>);

    const listItems = testedComponent.find("ListGroupItem");
    expect(listItems.at(0).text()).toEqual("collecting_potatoes");
    expect(listItems.at(0)).toHaveProperty("disabled", false);
    expect(listItems.at(1).text()).toEqual("collecting_grapes");
    expect(listItems.at(1)).toHaveProperty("disabled", true);
  });

  it('Should render simple list with one not selected item.', () => {
    const requestStateMock = jest.fn();
    const onSelectMock = jest.fn();

    const testedComponent = mount(<ActionsList actionsList={actionsList}
                                               requestState={requestStateMock}
                                               onSelectAction={onSelectMock}/>);

    const firstTestedItem = testedComponent.find("ListGroupItem").first();
    firstTestedItem.simulate("click");
    expect(onSelectMock).toHaveProperty("callCount", 1);
    expect(firstTestedItem).toHaveProperty("active", false);
    const testedSelectedComponent = mount(<ActionsList actionsList={actionsList}
                                                       requestState={requestStateMock}
                                                       selectedRecipeId="FIRST"
                                                       onSelectAction={onSelectMock}/>);
    const selectedTestedItem = testedSelectedComponent.find("ListGroupItem").first();
    expect(selectedTestedItem).toHaveProperty("active", true);
  });
});
