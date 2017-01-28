import React from "react";
import Entities from "../../commons/entities/Entities";
import {Panel} from "react-bootstrap";

class InventoryList extends React.Component {

  constructor(props) {
    super(props);
  }

  componentDidMount() {
    this.props.requestState();
  }

  componentDidUpdate(prevProps) {
    if (prevProps.characterId !== this.props.characterId) {
      this.props.requestState();
    }
  }

  render() {
    return <Panel header="Inventory">
      <Entities entities={this.props.itemsInInventory} {...this.props}/>
    </Panel>;
  }
}

export default InventoryList;
