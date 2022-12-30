package models

import "time"

type CollectionDate struct {
	time.Time
}

func (d *CollectionDate) MarshalJSON() ([]byte, error) {
	b := []byte(d.Time.Format(`"2006-01-02"`))
	return b, nil
}

func CollectionDateFromTime(time time.Time) *CollectionDate {
	return &CollectionDate{Time: time}
}
