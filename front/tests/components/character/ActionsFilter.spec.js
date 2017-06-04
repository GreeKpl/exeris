import * as Immutable from "immutable";
import {mount} from "enzyme";
import * as React from "react";
import {ActionsFilter} from "../../../src/components/character/actions/ActionsFilterContainer";

describe('(component) ActionsList', () => {

  it('Should render empty list when no data specified.', () => {
    const onChangeSpy = sinon.spy();
    const testedComponent = mount(<ActionsFilter filterText=""
                                                 onChange={onChangeSpy}/>);

    expect(testedComponent.find("input").text()).to.equal("");
    testedComponent.find("input").simulate('change', {target: {value: 'example'}});
    expect(onChangeSpy).to.have.property("callCount", 1);
  });
});
