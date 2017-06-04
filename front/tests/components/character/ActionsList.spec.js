import * as Immutable from "immutable";
import {mount} from "enzyme";
import * as React from "react";
import {ActionsList} from "../../../src/components/character/actions/ActionsListContainer";

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
    const requestStateSpy = sinon.spy();
    const testedComponent = mount(<ActionsList actionsList={Immutable.Map()}
                                               requestState={requestStateSpy}/>);

    expect(testedComponent.find("ListGroup").children()).to.have.length(0);
    expect(requestStateSpy).to.have.property("callCount", 1);
  });

  it('Should render simple list with one enabled and one disabled action.', () => {
    const requestStateSpy = sinon.spy();

    const testedComponent = mount(<ActionsList actionsList={actionsList}
                                               requestState={requestStateSpy}/>);

    const listItems = testedComponent.find("ListGroupItem");
    expect(listItems.at(0).text()).to.equal("collecting_potatoes");
    expect(listItems.at(0)).to.have.prop("disabled", false);
    expect(listItems.at(1).text()).to.equal("collecting_grapes");
    expect(listItems.at(1)).to.have.prop("disabled", true);
  });

  it('Should render simple list with one not selected item.', () => {
    const requestStateSpy = sinon.spy();
    const onSelectSpy = sinon.spy();

    const testedComponent = mount(<ActionsList actionsList={actionsList}
                                               requestState={requestStateSpy}
                                               onSelectAction={onSelectSpy}/>);

    const firstTestedItem = testedComponent.find("ListGroupItem").first();
    firstTestedItem.simulate("click");
    expect(onSelectSpy).to.have.property("callCount", 1);
    expect(firstTestedItem).to.have.prop("active", false);
    const testedSelectedComponent = mount(<ActionsList actionsList={actionsList}
                                                       requestState={requestStateSpy}
                                                       selectedRecipeId="FIRST"
                                                       onSelectAction={onSelectSpy}/>);
    const selectedTestedItem = testedSelectedComponent.find("ListGroupItem").first();
    expect(selectedTestedItem).to.have.prop("active", true);
  });
});
