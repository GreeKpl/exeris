import {mount} from "enzyme";
import * as React from "react";
import {ActionsFilter} from "../ActionsFilterContainer";

describe('(component) ActionsFilter', () => {

  it('Should render empty list when no data specified.', () => {
    const onChangeMock = jest.fn();
    const testedComponent = mount(<ActionsFilter filterText=""
                                                 onChange={onChangeMock}/>);

    expect(testedComponent.find("input").text()).toEqual("");
    testedComponent.find("input").simulate('change', {target: {value: 'example'}});
    expect(onChangeMock).toHaveBeenCalled();
  });
});
