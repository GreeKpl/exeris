import React from "react";
import "./style.scss";

class DynamicName extends React.Component {
  render() {
    return <span className="DynamicName-clickable" onClick={this.props.onClick}>
      {this.props.name}
      </span>;
  }
}

export default DynamicName;
