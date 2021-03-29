import Rete from 'rete'
import TextArea from '../vue-control-components/TextArea'

class TextAreaControl extends Rete.Control {
  constructor (name, emitter, label) {
    super(name)
    this.component = TextArea
    this.props = { name, ikey: name, emitter, label }
  }

  setValue (val) {
    this.vueContext.value = val
  }
}

export default TextAreaControl
