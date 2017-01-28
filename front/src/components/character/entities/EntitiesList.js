import React from "react";
import Entities from "../../commons/entities/Entities";


class EntitiesList extends React.Component {

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
    return <Entities entities={this.props.rootEntities} {...this.props}/>;
  }
}

export default EntitiesList;
