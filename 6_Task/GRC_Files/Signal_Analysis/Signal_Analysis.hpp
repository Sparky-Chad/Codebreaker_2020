#ifndef SIGNAL_ANALYSIS_HPP
#define SIGNAL_ANALYSIS_HPP
/********************
GNU Radio C++ Flow Graph Header File

Title: Not titled yet
Author: root
GNU Radio version: 3.8.2.0
********************/

/********************
** Create includes
********************/
#include <gnuradio/top_block.h>
#include <gnuradio/analog/sig_source.h>
#include <gnuradio/blocks/file_source.h>
#include <gnuradio/blocks/float_to_complex.h>
#include <gnuradio/blocks/throttle.h>
#include <gnuradio/qtgui/freq_sink_c.h>
#include <gnuradio/filter/firdes.h>

#include <QVBoxLayout>
#include <QScrollArea>
#include <QWidget>
#include <QGridLayout>
#include <QSettings>


using namespace gr;



class Signal_Analysis : public QWidget {
    Q_OBJECT

private:
    QVBoxLayout *top_scroll_layout;
    QScrollArea *top_scroll;
    QWidget *top_widget;
    QVBoxLayout *top_layout;
    QGridLayout *top_grid_layout;
    QSettings *settings;


    qtgui::freq_sink_c::sptr qtgui_freq_sink_x_0;
    blocks::throttle::sptr blocks_throttle_0;
    blocks::float_to_complex::sptr blocks_float_to_complex_0;
    blocks::file_source::sptr blocks_file_source_0;
    analog::sig_source_f::sptr analog_const_source_x_0;


// Variables:
    int samp_rate = 32000;

public:
    top_block_sptr tb;
    Signal_Analysis();
    ~Signal_Analysis();

    int get_samp_rate () const;
    void set_samp_rate(int samp_rate);

};


#endif

